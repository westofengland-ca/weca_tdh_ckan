"""
Tests for auth.py
"""

import pytest
import unittest
import json
import ckanext.weca_tdh.tests.config as test_config
import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.auth import ADAuth

class Auth(unittest.TestCase):
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

        claims_map = ADAuth.map_user_claims(claims)
        claims_map[C.CKAN_USER_ID] = test_config.TEST_AD_PRINCIPAL_ID
        claims_map[C.CKAN_USER_NAME] = test_config.TEST_AD_PRINCIPAL_NAME
        assert claims_map == user_map

        # Scenario where a claim is invalid
        encoded_token = test_config.TEST_AD_ID_TOKEN_MISSING_CLAIMS
        token = ADAuth.decode_token(encoded_token)

        user_info = json.loads(token)
        claims = user_info.get("claims", [])

        claims_map = ADAuth.map_user_claims(claims)
        claims_map[C.CKAN_USER_ID] = test_config.TEST_AD_PRINCIPAL_ID
        claims_map[C.CKAN_USER_NAME] = test_config.TEST_AD_PRINCIPAL_NAME
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
