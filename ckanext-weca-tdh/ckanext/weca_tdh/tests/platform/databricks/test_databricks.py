"""
Tests for databricks
"""

import logging
import os
import tempfile
import uuid
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests
from ckanext.weca_tdh.platform.databricks.download import download_file_from_url
from ckanext.weca_tdh.platform.databricks.utils import oauth_code_verify_and_challenge
from ckanext.weca_tdh.platform.databricks.views import databricksbp
from ckanext.weca_tdh.platform.databricks.workspace import (
    DatabricksWorkspace,
    redis_client,
)
from ckanext.weca_tdh.upload import BlobStorage
from flask import Flask

log = logging.getLogger(__name__)


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(databricksbp)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    return app.test_client()


@patch("uuid.uuid4")
def test_oauth_code_verify_and_challenge(mock_uuid):
    mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")
    code_verifier, code_challenge = oauth_code_verify_and_challenge()

    assert code_verifier == "12345678-1234-5678-1234-567812345678-12345678-1234-5678-1234-567812345678"
    assert isinstance(code_challenge, str)
    assert len(code_challenge) > 0


@patch("requests.get")
def test_download_file_from_url_success(mock_get):
    task_id = "test_task"
    file_url = "http://example.com/file.txt"
    output_path = "test_file.txt"
    access_token = "test_token"
    file_content = b"This is a test file."
    
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.iter_content = lambda chunk_size: [file_content] 
    
    mock_get.return_value.__enter__.return_value = mock_response

    with patch('builtins.open', mock_open()) as mock_file:
        download_file_from_url(task_id, file_url, output_path, access_token)
        
        task_info = redis_client.get_download_status(task_id)
        
        assert task_info["status"] == "completed"
        assert task_info["message"] == "Download completed."
        assert task_info["file_path"] == output_path
        
        mock_file.assert_called_once_with(output_path, 'wb')
        
    # cleanup
    redis_client.delete_download_task(task_id)
    assert redis_client.get_download_status(task_id) == {}


@pytest.mark.parametrize("status_code, expected_message", [
    (400, "invalid request"),
    (401, "unauthorized access"),
    (403, "unauthorized access"),
    (404, "file not available")
])
@patch("requests.get")
def test_download_file_from_url_http_error(mock_get, status_code, expected_message):
    task_id = "test_task"
    file_url = "http://example.com/file.txt"
    output_path = "test_file.txt"
    access_token = "test_token"
    
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)

    mock_get.return_value.__enter__.return_value = mock_response

    download_file_from_url(task_id, file_url, output_path, access_token)
    
    task_info = redis_client.get_download_status(task_id)

    assert task_info["status"] == "error"
    assert f"Download failed: {expected_message}. Contact the Data Owner for support." in task_info["message"]
    
    # cleanup
    redis_client.delete_download_task(task_id)
    assert redis_client.get_download_status(task_id) == {}


@patch("requests.get")
def test_download_file_from_url_other_exception(mock_get):
    task_id = "test_task"
    file_url = "http://example.com/file.txt"
    output_path = "test_file.txt"
    access_token = "test_token"
    error_message = "Some other error"

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception(error_message)

    mock_get.return_value.__enter__.return_value = mock_response

    download_file_from_url(task_id, file_url, output_path, access_token)
    
    task_info = redis_client.get_download_status(task_id)
        
    assert task_info["status"] == "error"
    assert task_info["message"] == f"Download failed: {error_message}."
    
    # cleanup
    redis_client.delete_download_task(task_id)
    assert redis_client.get_download_status(task_id) == {}


def test_get_task_status_success(client):
    task_id = "test_task"
    redis_client.set_download_status(task_id, status="completed", message="Done.")
    response = client.post("/databricks/download/status", json={"task_id": task_id})

    assert response.status_code == 200
    assert response.json["status"] == "completed"
    
    # cleanup
    redis_client.delete_download_task(task_id)
    assert redis_client.get_download_status(task_id) == {}


def test_get_task_status_not_found(client):
    task_id = "test_task"
    response = client.post("/databricks/download/status", json={"task_id": task_id})

    assert response.status_code == 404
    assert response.json["status"] == "not_found"


@patch("ckanext.weca_tdh.platform.databricks.download.toolkit.redirect_to")
@patch("ckanext.weca_tdh.platform.databricks.download.flash")
def test_download_file(mock_flash, mock_redirect, client):
    task_id = "test_task"
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name
        temp_file.write(b"This is a test file.")

        redis_client.set_download_status(task_id, status="completed", message="Download completed.", file_path=file_path)

        response = client.get(f"/databricks/download/{task_id}")
        assert response.status_code == 200
        
        assert redis_client.get_download_status(task_id) == {}
        assert not os.path.exists(file_path)

        mock_flash.assert_not_called()
        mock_redirect.assert_not_called()


@patch("ckanext.weca_tdh.platform.databricks.download.toolkit.redirect_to")
@patch("ckanext.weca_tdh.platform.databricks.download.flash")
def test_download_file_not_found(mock_flash, mock_redirect, client):
    task_id = "test_task"
    redis_client.set_download_status(task_id, status="completed", message="Download completed.", file_path="/tmp/missing_file")
    
    client.get(f"/databricks/download/{task_id}")

    assert redis_client.get_download_status(task_id) == {}

    mock_flash.assert_called_once_with("Failed to download file: file not found.", category="alert-danger")
    mock_redirect.assert_called_once_with("/")
    

@patch("ckanext.weca_tdh.platform.databricks.download.toolkit.redirect_to")
@patch("ckanext.weca_tdh.platform.databricks.download.flash")
def test_download_file_missing_task_id(mock_flash, mock_redirect, client):
    client.get("/databricks/download/test_task")

    mock_flash.assert_called_once_with("Failed to download file: Task ID not found.", category="alert-danger")
    mock_redirect.assert_called_once_with("/")


@patch.object(BlobStorage, "download_blob_as_json", return_value={"catalog_files": {"resource-1": {"file_name": "test.csv", "catalog_name": "cat", "schema_name": "sch", "volume_name": "vol"}}})
@patch.object(DatabricksWorkspace, "get_workspace_access_token", return_value="test-token")
def test_start_download(mock_get_token, mock_blob, client):
    response = client.post("/databricks/download/start", json={"resource_id": "resource-1"})

    assert response.status_code == 200
    assert response.json["message"] == "Download started."
