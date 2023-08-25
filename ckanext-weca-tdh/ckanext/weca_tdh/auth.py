import base64
import json
import logging
from ckanext.weca_tdh.user import User
import ckanext.weca_tdh.config as C
import ckan.lib.helpers as h
from ckan.common import config
from flask import request, Blueprint

log = logging.getLogger(__name__)
authbp = Blueprint('auth', __name__,)

class ADAuth():
    
    @authbp.route("/auth/aad")
    def login():
        try:
            claims_map = ADAuth.map_user_claims()
            if claims_map:
                # get or create user obj
                user = User.get_or_create_ad_user(claims_map)

                # start user session
                User.start_session(user)

                # redirect to landing page
                return h.redirect_to('/')

        except Exception as e:
            log.error(f"Login failed: {e}")
            return h.redirect_to('user.login')

    def map_user_claims():
        claims_map = {}

        claims_map[C.CKAN_USER_ID] = request.headers.get(C.AD_USER_ID)      
        claims_map[C.CKAN_USER_NAME] = request.headers.get(C.AD_USER_NAME)

        # decode base64 access token
        try:
            token = ADAuth.decode_token(request.headers.get(C.AD_ID_TOKEN))
        except Exception as e:
            raise Exception(f"Invalid AD access token: {e}")

        user_info = json.loads(token)
        claims = user_info.get("claims", [])

        # map claims to ckan user obj
        if claims:          
            claim_url = C.AD_CLAIM_URL
            for claim in claims:
                claim_type = claim.get(C.AD_CLAIM_TYPE)
                claim_value = claim.get(C.AD_CLAIM_VALUE)

                if claim_type == f"{claim_url}/{C.AD_CLAIM_EMAIL}":
                    claims_map[C.CKAN_USER_EMAIL] = claim_value

                elif claim_type == f"{claim_url}/{C.AD_CLAIM_GIVEN_NAME}":
                    claims_map[C.CKAN_USER_GIVEN_NAME] = claim_value

                elif claim_type == f"{claim_url}/{C.AD_CLAIM_SURNAME}":
                    claims_map[C.CKAN_USER_SURNAME] = claim_value

                elif claim_type == C.AD_CLAIM_GROUPS:
                    if claim_value == C.AD_GROUP_SYSADMIN_ID and config[C.FF_AD_SYSADMIN] == 'True':
                        claims_map[C.CKAN_ROLE_SYSADMIN] = True

        return claims_map

    def decode_token(token):
        return base64.b64decode(token + '==').decode('utf-8')
    
    def get_blueprint():
        return authbp
