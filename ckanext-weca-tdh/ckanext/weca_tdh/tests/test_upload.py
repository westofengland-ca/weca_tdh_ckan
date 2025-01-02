"""
Tests for upload.py
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from flask import Flask, get_flashed_messages, session
from flask.sessions import SecureCookieSessionInterface

import ckanext.weca_tdh.config as C
import ckanext.weca_tdh.upload as Upload

mock_signiture_body = {
        "upload_date": "01-01-2025_12:00:00",
        "author": "Test Author",
        "author_email": "author@test.com",
        "description": "Test Description",
        "resource_id": "resource_id",
        "resource_name": "Test Resource",
        "dataset_id": "package_id",
        "dataset_name": "dataset_id",
        "dataset_title": "Test Dataset",
        "publisher_id": "org_id",
        "publisher_name": "org_name",
        "publisher_title": "org_title",
    }

def test_verify_file_valid():
    valid_filename = "test.csv"
    valid_file_size = 1024  # within size limit

    with patch("ckanext.weca_tdh.config.TDH_UPLOAD_FILE_TYPES", [".csv"]):
        with patch("ckanext.weca_tdh.config.TDH_UPLOAD_FILE_SIZE", 2048):
            Upload.verify_file(valid_filename, valid_file_size)  # Should not raise any exceptions

def test_verify_file_invalid_type():
    invalid_filename = "test.txt"
    valid_file_size = 1024

    with patch("ckanext.weca_tdh.config.TDH_UPLOAD_FILE_TYPES", [".csv"]):
        with pytest.raises(Exception, match="Unsupported file type."):
            Upload.verify_file(invalid_filename, valid_file_size)

def test_verify_file_invalid_size():
    valid_filename = "test.csv"
    invalid_file_size = 4096

    with patch("ckanext.weca_tdh.config.TDH_UPLOAD_FILE_TYPES", [".csv"]):
        with patch("ckanext.weca_tdh.config.TDH_UPLOAD_FILE_SIZE", 2048):
            with pytest.raises(Exception, match="File size too large."):
                Upload.verify_file(valid_filename, invalid_file_size)


def test_create_signiture_body():
    mock_request = Mock()
    mock_request.form = {
        "author": "Test Author",
        "author_email": "author@test.com",
        "desc": "Test Description",
    }

    with patch("ckanext.weca_tdh.upload.request", mock_request):
        body = Upload.create_signiture_body(
            "dataset_id",
            "resource_id",
            {
                "resource": {"name": "Test Resource", "package_id": "package_id"},
                "pkg_dict": {
                    "title": "Test Dataset",
                    "organization": {
                        "id": "org_id",
                        "name": "org_name",
                        "title": "org_title",
                    },
                },
            },
            "01-01-2025_12:00:00",
        )

    assert body == mock_signiture_body

def test_generate_signiture_file(tmp_path):
    file_path = tmp_path / "info.json"
    body = {"key": "value"}

    Upload.generate_signiture_file(str(file_path), body)

    with open(file_path, "r") as f:
        content = f.read()

    assert content == '{"key": "value"}'


def test_call_http_trigger_success():
    body = {"key": "value"}
    mock_response = Mock(ok=True)

    with patch("requests.post", return_value=mock_response) as mock_post:
        Upload.call_http_trigger(body)
        mock_post.assert_called_once_with(C.TDH_UPLOAD_HTTP_TRIGGER, json=body)

def test_call_http_trigger_failure():
    body = {"key": "value"}
    mock_response = Mock(ok=False, status_code=500)

    with patch("requests.post", return_value=mock_response):
        with pytest.raises(Exception, match="HTTP trigger status code 500"):
            Upload.call_http_trigger(body)


def test_blob_storage_upload_blob():
    mock_blob_service_client = Mock()
    mock_blob_client = Mock()
    mock_blob_service_client.get_blob_client.return_value = mock_blob_client

    with patch.object(Upload.BlobStorage, "get_blob_service_client", return_value=mock_blob_service_client):
        Upload.BlobStorage().upload_blob(b"file content", "test.zip")

    mock_blob_service_client.get_blob_client.assert_called_once_with(
        container=C.TDH_UPLOAD_STORAGE_CONTAINER, blob="test.zip"
    )
    mock_blob_client.upload_blob.assert_called_once_with(b"file content")

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app

def test_blob_upload_view_get(app):
    view = Upload.BlobUploadView()
    mock_toolkit = Mock()
    mock_toolkit.render.return_value = "Rendered Template"

    with patch("ckanext.weca_tdh.upload.toolkit", mock_toolkit):
        with app.test_request_context():
            response = view.get("dataset_id", "resource_id")

    assert response == "Rendered Template"

def test_blob_upload_view_post(app):
    # Configure the app for sessions
    app.secret_key = "test-secret-key"
    app.session_interface = SecureCookieSessionInterface()
    
    view = Upload.BlobUploadView()
    mock_toolkit = Mock()
    mock_toolkit.redirect_to.return_value = "Redirected"
    
    # Mock the uploaded file
    mock_file = Mock()
    mock_file.filename = "tester.csv"
    mock_file.tell.return_value = 1024
    mock_file.seek.return_value = None
    mock_file.save.side_effect = lambda path: Path(path).write_text("dummy content")
    
    # Mock `generate_signiture_file` to create info.json
    def mock_generate_signiture_file(file_path, body):
        Path(file_path).write_text("{\"key\": \"value\"}")
    
    with patch("tempfile.TemporaryDirectory") as mock_tempdir:
        tempdir = Path("/tmp/mock_tempdir")
        tempdir.mkdir(parents=True, exist_ok=True)
        mock_tempdir.return_value.__enter__.return_value = str(tempdir)

        with patch("ckanext.weca_tdh.upload.toolkit", mock_toolkit):
            with patch("ckanext.weca_tdh.upload.get_request_file", return_value=(mock_file, "test.csv", 1024)):
                with patch("ckanext.weca_tdh.upload.create_signiture_body", return_value=mock_signiture_body):
                    with patch("ckanext.weca_tdh.upload.generate_signiture_file", side_effect=mock_generate_signiture_file):
                        with patch("ckanext.weca_tdh.upload.BlobStorage.upload_blob"):
                            with patch("ckanext.weca_tdh.upload.call_http_trigger"):
                                with app.test_request_context():
                                    session['csrf_token'] = 'test-token'
                                    response = view.post("dataset_id", "resource_id")
                                    flashed_messages = get_flashed_messages(with_categories=True)
                                        
    # Assert a success flash message was added
    success_messages = [msg for category, msg in flashed_messages if category == "alert-success"]
    assert len(success_messages) > 0
    assert C.UPLOAD_STATUS_SUCCESS in success_messages[0]
    
    assert response == "Redirected"
