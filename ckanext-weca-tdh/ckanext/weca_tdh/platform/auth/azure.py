import base64
import itertools
import json
import logging
from typing import Any

import ckan.authz as authz
import ckan.plugins.toolkit as toolkit
import ckanext.weca_tdh.config as C
import requests
from ckan import model
from ckan.types import Context
from ckan.views.user import _extra_template_variables
from ckanext.weca_tdh.platform.auth.user import User
from ckanext.weca_tdh.platform.redis_config import RedisConfig
from flask import Blueprint, flash, request
from flask.views import MethodView

log = logging.getLogger(__name__)
adauthbp = Blueprint('adauth', __name__)
redis_client = RedisConfig(C.REDIS_URL)

BATCH_LIMIT = 20


class UserAuthError(Exception):
    pass


class ADAuth(object):
    """Handles AD user authorisation"""

    def authorise(self) -> None:
        """
        Authenticate user via AD token and log them in.
        Returns a Flask redirect response.
        """
        try:
            claims = self.get_user_claims()
            if claims:
                username = User.get_or_create_ad_user(claims)
                self.login_to_ckan(username)

            referrer = request.args.get('referrer', default='dashboard.datasets')

            if referrer == toolkit.url_for('user.login'):
                referrer = 'dashboard.datasets'
            return toolkit.redirect_to(referrer)
        
        except Exception as e:
            log.exception(f"Authorisation failed: {e}")

            if isinstance(e, UserAuthError):
                flash(f"Authorisation failed: {e} {C.ALERT_MESSAGE_SUPPORT}.", category='alert-danger')
            else:
                flash(f"Failed to login. {C.ALERT_MESSAGE_SUPPORT}.", category='alert-danger')

            return toolkit.redirect_to('user.login')


    def get_user_claims(self) -> dict[str, Any]:
        """Decode AD token and map claims to CKAN user obj."""
        try:
            token = self.decode_token(request.headers.get(C.AD_ID_TOKEN))
        except Exception:
            raise Exception('invalid AD access token.')

        user_info = json.loads(token)
        claims = user_info.get('claims', {})

        if not claims:
            raise Exception("No claims found in token.")

        user_id = request.headers.get(C.AD_USER_ID)

        if not user_id:
            raise Exception("AD User ID header missing.")

        return self.map_user_claims(claims, user_id)


    def map_user_claims(self, claims: dict, user_id: str) -> dict[str, Any]:
        """
        Maps AD claims to CKAN user obj.
        Resolves group IDs to names using Graph API + Redis caching.
        """
        claims_map = {
            C.CKAN_USER_ID: user_id,
            C.AD_USER_GROUPS: []
        }
        id_claim_url = C.AD_CLAIM_ID_URL
        claim_url = C.AD_CLAIM_URL
        in_user_group = False
        aud = ""
        tenant_id = ""
        group_ids = []

        for claim in claims:
            claim_type = claim.get(C.AD_CLAIM_TYPE)
            claim_value = claim.get(C.AD_CLAIM_VALUE)
            
            if claim_type == C.AD_CLAIM_AUDIENCE:
                aud = claim_value
            elif claim_type == f"{id_claim_url}/{C.AD_CLAIM_TENANT}":
                tenant_id = claim_value
            elif claim_type == C.AD_CLAIM_NAME:
                claims_map[C.CKAN_USER_FULLNAME] = claim_value
            elif claim_type == f"{claim_url}/{C.AD_CLAIM_EMAIL}":
                claims_map[C.CKAN_USER_EMAIL] = claim_value
            elif claim_type == C.AD_CLAIM_GROUPS:
                if claim_value == C.AD_GROUP_CKAN_ID:
                    in_user_group = True
                elif claim_value == C.AD_GROUP_SYSADMIN_ID and C.FF_AD_SYSADMIN == 'True':
                    claims_map[C.CKAN_ROLE_SYSADMIN] = True
                else:
                    group_ids.append(claim_value)

        access_token = self.get_graph_token(aud, tenant_id)
        claims_map[C.AD_USER_GROUPS] = self.resolve_group_names(group_ids, access_token)

        if C.FF_AUTH_USER_GROUP_ONLY == 'True' and not in_user_group:
           raise UserAuthError('account not in authorised user group.')

        return claims_map


    @staticmethod
    def get_graph_token(aud: str, tenant_id: str):
        """Obtain an Azure AD Graph API token for the app."""
        token = ""
        
        if not aud or not tenant_id:
            log.warning("Auth: Missing audience or tenant ID for Graph token.")
            return token
        
        cache_key = f"graph_token:{tenant_id}:{aud}"
        try:
            cached_token = redis_client.client.get(cache_key)
            if cached_token:
                return cached_token
        except Exception as e:
            log.warning(f"Auth: Redis unavailable, skipping cache lookup. {e}")
        
        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": aud,
            "client_secret": C.TDH_AD_APP_CLIENT_SECRET,
            "scope": "https://graph.microsoft.com/.default"
        }
        
        try:
            resp = requests.post(url, data=data)
            resp.raise_for_status()
            resp_json = resp.json()
            token = resp_json.get("access_token")

            expires_in = int(resp_json.get("expires_in", 3600))
            ttl = max(1, expires_in - 300)
            redis_client.client.set(cache_key, token, ex=ttl)

            return token
        
        except Exception as e:
            log.warning(f"Auth: Failed to obtain Graph API token. {e}", exc_info=True)
        
        return token


    def resolve_group_names(self, group_ids: list, access_token: str) -> list:
        """
        Resolves AD group IDs to names using Microsoft Graph API with batch requests.
        Uses a global Redis cache for all users.
        """
        resolved = []
        to_fetch = []
        
        if not access_token:
            log.warning("Auth: Missing or invalid Graph API token. Skipping group name resolution.")
            return resolved

        for gid in group_ids:
            try:
                name = redis_client.get_group_name(gid)
            except Exception as e:
                log.warning(f"Auth: Redis unavailable, skipping group cache lookup for {gid}. {e}")
                name = None

            if name:
                resolved.append({"id": gid, "name": name})
            else:
                to_fetch.append(gid)
         
        if not to_fetch:
            return resolved

        for batch_index, batch in enumerate(self._chunks(to_fetch, BATCH_LIMIT)):
            batch_requests = [
                {"id": str(i), "method": "GET", "url": f"/groups/{gid}?$select=displayName"}
                for i, gid in enumerate(batch)
            ]

            try:
                resp = requests.post(
                    "https://graph.microsoft.com/v1.0/$batch",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={"requests": batch_requests}
                )

                resp.raise_for_status()
                results = resp.json().get("responses", [])

                for res in results:
                    gid = batch[int(res["id"])]
                    if res.get("status") == 200:
                        display_name = res["body"]["displayName"]
                    else:
                        display_name = gid
                    if str(display_name).startswith("tdh_"):
                        resolved.append({"id": gid, "name": display_name})
                        redis_client.set_group_name(gid, display_name)
            
            except Exception as e:
                log.warning(f"Auth: Failed to resolve group names via Graph API. {e}", exc_info=True)

        return resolved


    @staticmethod
    def _chunks(iterable, size):
        """Yield successive n-sized chunks from iterable."""
        it = iter(iterable)
        while True:
            chunk = list(itertools.islice(it, size))
            if not chunk:
                break
            yield chunk


    @staticmethod
    def decode_token(token: str) -> str:
        """Decode base64-encoded AD token"""
        return base64.b64decode(token + '==').decode('utf-8')


    @staticmethod
    def login_to_ckan(username: str) -> None:
        userobj = model.User.get(username)
        if not userobj:
            raise Exception(f"User {username} not found.")
        toolkit.login_user(userobj, force=True)


class UserGroupsView(MethodView):
    """List AD security groups for a user"""
    def get(self, id: str):
        current_user_obj = toolkit.current_user
        current_user = current_user_obj.name
        viewed_user = id
        is_myself = current_user == viewed_user
        is_sysadmin = authz.is_sysadmin(current_user)
        
        if not (is_myself or is_sysadmin):
            toolkit.abort(403, 'Not authorised to see this page')
            
        context: Context = {
            u'user': current_user,
            u'auth_user_obj': current_user_obj,
            u'for_view': True,
            u'include_plugin_extras': True,
        }
        
        data_dict: dict[str, Any] = {u'id': id}
        extra_vars = _extra_template_variables(context, data_dict)
            
        user_obj = model.User.get(viewed_user)
        plugin_extras = user_obj.plugin_extras or {}
        access_groups = plugin_extras.get('ad_groups', [])
        
        extra_vars['plugin_extras'] = plugin_extras
        extra_vars['ad_groups'] = access_groups

        return toolkit.render('user/read_access_groups.html', extra_vars)


adauthbp.add_url_rule('/user/adlogin', view_func=ADAuth().authorise)

adauthbp.add_url_rule(
    "/user/<id>/access-groups",
    view_func=UserGroupsView.as_view(str("read_access_groups")),
)
