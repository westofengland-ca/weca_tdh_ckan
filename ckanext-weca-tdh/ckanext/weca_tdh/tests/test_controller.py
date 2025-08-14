"""
Tests for controller.py
"""
import json
from unittest.mock import patch

from flask import Flask

from ckanext.weca_tdh.controller import Controller

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
                "Catalog": "bronze_development",
                "Database": "transport_data"
            },
            "mode": "DirectQuery"
        }
    ]
}

@patch("ckanext.weca_tdh.controller.C.TDH_CONNECT_ADDRESS_HOST", mock_host)
@patch("ckanext.weca_tdh.controller.C.TDH_CONNECT_ADDRESS_PATH", mock_path)
def test_download_tdh_partner_connect_file():
    app = Flask(__name__)
    with app.test_request_context("/tdh_partner_connect_file?tdh_catalog=bronze_development&tdh_schema=transport_data"):
        result = Controller.download_tdh_partner_connect_file()
        assert json.loads(result) == mock_file