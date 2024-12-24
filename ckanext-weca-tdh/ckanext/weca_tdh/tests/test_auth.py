"""
Tests for auth.py
"""

import pytest
import unittest
from unittest.mock import patch
import json
import ckanext.weca_tdh.tests.config as test_config
import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.auth import ADAuth


class Auth(unittest.TestCase):

    def test_map_user_claims(self) -> None:
        # Test mapping of claims to ckan user obj
        user_map = {
            'id': '5f43883e-63a8-4dc6-a070-b27681a5d057',
            'email': 'mock.user@test.co.uk',
            'fullname': 'Mock User'
        }

        # Scenario where all claims are valid
        encoded_token = test_config.TEST_AD_ID_TOKEN
        token = ADAuth.decode_token(encoded_token)

        user_info = json.loads(token)
        claims = user_info.get("claims", [])

        claims_map = ADAuth.map_user_claims(claims)
        claims_map[C.CKAN_USER_ID] = test_config.TEST_AD_PRINCIPAL_ID
        assert claims_map == user_map

        # Scenario where a user is not in the user group
        with patch.object(C, 'AD_GROUP_CKAN_ID', ''):
            with pytest.raises(Exception):
                claims_map = ADAuth.map_user_claims(claims)

        # Scenario where sysadmin is set
        with patch.object(C, 'FF_AD_SYSADMIN', 'True'):
            claims_map = ADAuth.map_user_claims(claims)
            claims_map[C.CKAN_USER_ID] = test_config.TEST_AD_PRINCIPAL_ID
            user_map[C.CKAN_ROLE_SYSADMIN] = True
            assert claims_map == user_map

        # Scenario where a claim is invalid
        encoded_token = test_config.TEST_AD_ID_TOKEN_MISSING_CLAIMS
        token = ADAuth.decode_token(encoded_token)

        user_info = json.loads(token)
        claims = user_info.get("claims", [])

        claims_map = ADAuth.map_user_claims(claims)
        claims_map[C.CKAN_USER_ID] = test_config.TEST_AD_PRINCIPAL_ID
        assert claims_map != user_map

    def test_decode_token(self) -> None:
        # Test decoding base64 id token

        # valid token
        encoded_token = test_config.TEST_AD_ID_TOKEN
        token = ADAuth.decode_token(encoded_token)
        assert token == test_config.TEST_TOKEN_DECODED

        # invalid token
        encoded_token_inv = test_config.TEST_AD_ID_TOKEN_INV
        with pytest.raises(Exception):
            token = ADAuth.decode_token(encoded_token_inv)
