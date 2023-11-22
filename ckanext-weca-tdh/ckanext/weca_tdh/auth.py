import base64
import json
import logging
from ckanext.weca_tdh.user import User
import ckanext.weca_tdh.config as C
from flask import request

log = logging.getLogger(__name__)

class ADAuth():
    def authorise():
        try:
            claims_map = ADAuth.get_user_claims()
            if claims_map:
                # get or create user obj
                user = User.get_or_create_ad_user(claims_map)

                # create user session
                User.create_session(user)

        except Exception as e:
            raise Exception(f"Authorisation failed: {e} {C.ALERT_MESSAGE_SUPPORT}.")

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
            raise Exception("account not in user group.")

        return claims_map

    def decode_token(token):
        return base64.b64decode(token + '==').decode('utf-8')
