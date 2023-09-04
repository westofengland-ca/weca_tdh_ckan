"""
Tests for auth.py
"""

import pytest
import unittest
import json
import ckanext.weca_tdh.tests.config as test_config
import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.auth import ADAuth
from ckan.common import config

class Auth(unittest.TestCase):

    def map_user_claims(self, claims):
        # Helper function to return mock claims map
        claims_map = {}
        claims_map['id'] = test_config.TEST_AD_PRINCIPAL_ID
        claims_map['name'] = test_config.TEST_AD_PRINCIPAL_NAME

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

    def test_map_user_claims(self):
        # Test mapping of claims to ckan user obj
        user_map = {
            'id': '5f43883e-63a8-4dc6-a070-b27681a5d057',
            'name': 'mock.user@email.co.uk',
            'email': 'mock.user@email.co.uk',
            'given_name': 'Mock',
            'surname': 'User'
        }

        # Scenario where all claims are valid
        encoded_token = test_config.TEST_AD_ID_TOKEN
        token = ADAuth.decode_token(encoded_token)

        user_info = json.loads(token)
        claims = user_info.get("claims", [])

        claims_map = self.map_user_claims(claims)
        assert claims_map == user_map

        # Scenario where a claim is invalid
        encoded_token = test_config.TEST_AD_ID_TOKEN_MISSING_CLAIMS
        token = ADAuth.decode_token(encoded_token)

        user_info = json.loads(token)
        claims = user_info.get("claims", [])

        claims_map = self.map_user_claims(claims)
        assert claims_map != user_map

    def test_decode_token(self):
        # Test decoding base64 id token
        
        # valid token
        encoded_token = test_config.TEST_AD_ID_TOKEN
        token = ADAuth.decode_token(encoded_token)
        assert token == test_config.TEST_TOKEN_DECODED

        # invalid token
        encoded_token_inv = test_config.TEST_AD_ID_TOKEN_INV
        with pytest.raises(Exception):
            token = ADAuth.decode_token(encoded_token_inv)
