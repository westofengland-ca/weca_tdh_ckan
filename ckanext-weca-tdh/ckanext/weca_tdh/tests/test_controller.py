"""
Tests for controller.py
"""
import json, pytest
from unittest.mock import patch
from ckanext.weca_tdh.controller import RouteController

mock_host = "mock.host"
mock_path = "mock/address/path"
mock_file = {
    "version": "0.1",
    "connections": [
        {
            "details": {
            "protocol": "databricks-sql",
            "address": {
                "host": mock_host,
                "path": mock_path
            },
            "authentication": None,
            "query": None
            },
            "options": {
            "Catalog": "",
            "Database": ""
            },
            "mode": "DirectQuery"
        }
    ]
}

@patch("ckanext.weca_tdh.controller.C.TDH_CONNECT_ADDRESS_HOST", mock_host)
@patch("ckanext.weca_tdh.controller.C.TDH_CONNECT_ADDRESS_PATH", mock_path)
def test_download_tdh_partner_connect_file() -> None:  
    json_file = RouteController.download_tdh_partner_connect_file()
    assert json_file == json.dumps(mock_file)