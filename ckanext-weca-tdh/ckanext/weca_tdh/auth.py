import ckan.model as model
import ckan.plugins.toolkit as toolkit
from flask import Blueprint, flash, request
import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.user import User
import base64, json, logging

log = logging.getLogger(__name__)
adauthbp = Blueprint('adauth', __name__)

class ADAuth():  
    def _login_to_ckan(user):
        userobj = model.User.get(user)
        toolkit.login_user(userobj, force=True)

    def authorise():
        try:
            claims_map = ADAuth.get_user_claims()
            if claims_map:
                user = User.get_or_create_ad_user(claims_map)

            ADAuth._login_to_ckan(user)
            referer = request.args.get('referrer', default='dashboard.datasets')

            if referer == toolkit.url_for('user.login'):
                return toolkit.redirect_to('dashboard.datasets')
            return toolkit.redirect_to(referer)

        except Exception as e:
            flash(f"Authorisation failed: {e} {C.ALERT_MESSAGE_SUPPORT}.", category='alert-danger')
            return toolkit.redirect_to('user.login')

    def get_user_claims():
        try:
            token = ADAuth.decode_token(request.headers.get(C.AD_ID_TOKEN)) # decode base64 access token
        except Exception:
            raise Exception(f"invalid AD access token.")

        user_info = json.loads(token)
        claims = user_info.get("claims", [])

        if claims:
            claims_map = ADAuth.map_user_claims(claims)
            claims_map[C.CKAN_USER_ID] = request.headers.get(C.AD_USER_ID)      
            return claims_map

    def map_user_claims(claims):
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
            raise Exception("account not in authorised user group.")

        return claims_map

    def decode_token(token):
        return base64.b64decode(token + '==').decode('utf-8')
    
adauthbp.add_url_rule('/user/adlogin', view_func=ADAuth.authorise)
