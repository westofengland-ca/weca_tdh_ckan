"""
Tests for azure.py
"""

import pytest
import unittest
from unittest.mock import patch
import json
import ckanext.weca_tdh.tests.config as test_config
import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.platform.auth.azure import ADAuth


class Auth(unittest.TestCase):

    @patch("ckanext.weca_tdh.platform.auth.azure.ADAuth.get_graph_token")
    @patch("ckanext.weca_tdh.platform.auth.azure.ADAuth.resolve_group_names")
    def test_map_user_claims(self, mock_resolve_groups, mock_get_token) -> None:
        
        # Mock dependencies
        mock_get_token.return_value = "mock_graph_token"
        mock_resolve_groups.return_value = [{"id": "g1", "name": "tdh_users"}]
        
        user_map = {
            "id": "5f43883e-63a8-4dc6-a070-b27681a5d057",
            "email": "mock.user@test.co.uk",
            "fullname": "Mock User"
        }

        # all claims valid
        encoded_token = test_config.TEST_AD_ID_TOKEN
        token = ADAuth.decode_token(encoded_token)
        claims = json.loads(token).get("claims", [])
        claims_map = ADAuth.map_user_claims(ADAuth, claims, user_map["id"])

        claims_map[C.CKAN_USER_ID] = test_config.TEST_AD_PRINCIPAL_ID
        assert claims_map[C.CKAN_USER_EMAIL] == user_map["email"]
        assert claims_map[C.CKAN_USER_FULLNAME] == user_map["fullname"]

        # user not in authorised group
        with patch.object(C, "AD_GROUP_CKAN_ID", ""):
            with pytest.raises(Exception):
                ADAuth.map_user_claims(ADAuth, claims, user_map["id"])

        # sysadmin flag set
        with patch.object(C, "FF_AD_SYSADMIN", "True"):
            claims_map = ADAuth.map_user_claims(ADAuth, claims, user_map["id"])
            claims_map[C.CKAN_USER_ID] = test_config.TEST_AD_PRINCIPAL_ID
            assert claims_map.get(C.CKAN_ROLE_SYSADMIN) is True

        # missing claim set
        encoded_token = test_config.TEST_AD_ID_TOKEN_MISSING_CLAIMS
        token = ADAuth.decode_token(encoded_token)
        claims = json.loads(token).get("claims", [])
        claims_map = ADAuth.map_user_claims(ADAuth, claims, user_map["id"])
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
