import base64
import json
import logging

import ckan.model as model
import ckan.plugins.toolkit as toolkit
from flask import Blueprint, flash, request

import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.platform.auth.user import User

log = logging.getLogger(__name__)
adauthbp = Blueprint('adauth', __name__)


class ADAuth(object):
    
    @classmethod
    def authorise(cls) -> None:
        try:
            claims_map = cls.get_user_claims()
            if claims_map:
                username = User.get_or_create_ad_user(claims_map)
                cls.login_to_ckan(username)

            referer = request.args.get('referrer', default='dashboard.datasets')

            if referer == toolkit.url_for('user.login'):
                return toolkit.redirect_to('dashboard.datasets')
            return toolkit.redirect_to(referer)

        except Exception as e:
            flash(f"Authorisation failed: {e} {C.ALERT_MESSAGE_SUPPORT}.", category='alert-danger')
            return toolkit.redirect_to('user.login')

    @classmethod
    def get_user_claims(cls) -> list:
        try:
            token = cls.decode_token(request.headers.get(C.AD_ID_TOKEN))
        except Exception:
            raise Exception('invalid AD access token.')

        user_info = json.loads(token)
        log.error(f"user_info: {user_info}")
        claims = user_info.get('claims', {})

        if claims:
            claims_map = cls.map_user_claims(claims)
            claims_map[C.CKAN_USER_ID] = request.headers.get(C.AD_USER_ID)      
            return claims_map

    @staticmethod
    def map_user_claims(claims: dict) -> dict:
        claims_map = {}
        claim_url = C.AD_CLAIM_URL
        in_user_group = False

        for claim in claims:
            claim_type = claim.get(C.AD_CLAIM_TYPE)
            claim_value = claim.get(C.AD_CLAIM_VALUE)

            if claim_type == C.AD_CLAIM_NAME:
                claims_map[C.CKAN_USER_FULLNAME] = claim_value

            if claim_type == f"{claim_url}/{C.AD_CLAIM_EMAIL}":
                claims_map[C.CKAN_USER_EMAIL] = claim_value

            elif claim_type == C.AD_CLAIM_GROUPS:
                if claim_value == C.AD_GROUP_CKAN_ID:
                    in_user_group = True
                elif claim_value == C.AD_GROUP_SYSADMIN_ID and C.FF_AD_SYSADMIN == 'True':
                    claims_map[C.CKAN_ROLE_SYSADMIN] = True

        if C.FF_AUTH_USER_GROUP_ONLY == 'True' and not in_user_group:
           raise Exception('account not in authorised user group.')

        return claims_map
    
    @staticmethod
    def login_to_ckan(username: str) -> None:
        userobj = model.User.get(username)
        toolkit.login_user(userobj, force=True)

    @staticmethod
    def decode_token(token: str) -> str:
        # decode base64 access token
        return base64.b64decode(token + '==').decode('utf-8')
    
adauthbp.add_url_rule('/user/adlogin', view_func=ADAuth().authorise)
