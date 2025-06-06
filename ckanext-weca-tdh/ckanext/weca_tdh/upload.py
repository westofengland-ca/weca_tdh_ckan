import json
import logging
import os
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

import ckan.plugins.toolkit as toolkit
import requests
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from flask import Blueprint, flash, request
from flask.views import MethodView

import ckanext.weca_tdh.config as C

log = logging.getLogger(__name__)
uploadbp = Blueprint("upload", __name__)


def call_http_trigger(body: dict) -> None:
    url = C.TDH_UPLOAD_HTTP_TRIGGER
    response = requests.post(url, json=body)

    if not response.ok:
        raise Exception(f"HTTP trigger status code {response.status_code}")


def create_signiture_body(id, resource_id, data_dict, timestamp) -> dict:
    body = {
        "upload_date": timestamp,
        "author": request.form["author"],
        "author_email": request.form["author_email"],
        "description": request.form["desc"],
        "resource_id": resource_id,
        "resource_name": data_dict["resource"]["name"],
        "dataset_id": data_dict["resource"]["package_id"],
        "dataset_name": id,
        "dataset_title": data_dict["pkg_dict"]["title"],
        "publisher_id": data_dict["pkg_dict"]["organization"]["id"],
        "publisher_name": data_dict["pkg_dict"]["organization"]["name"],
        "publisher_title": data_dict["pkg_dict"]["organization"]["title"],
    }

    return body


def generate_signiture_file(file_path: str, body: dict) -> None:
    with open(file_path, "w") as file:
        json.dump(body, file)


def get_request_file() -> tuple[any, str, int]:
    upload_file = request.files["file"]
    upload_file.seek(0, os.SEEK_END)
    filename = upload_file.filename
    filesize = upload_file.tell()

    return upload_file, filename, filesize


def verify_file(filename: str, file_size: int) -> None:
    # get file extension
    _, ext = os.path.splitext(filename)

    if ext not in C.TDH_UPLOAD_FILE_TYPES:
        raise Exception("Unsupported file type.")

    if file_size > C.TDH_UPLOAD_FILE_SIZE:
        raise Exception("File size too large.")


class BlobStorage:
    """Manage Azure Blob Storage client"""

    @staticmethod
    def get_blob_service_client():
        account_url = f"https://{C.TDH_UPLOAD_STORAGE_ACCOUNT}.blob.core.windows.net"
        default_credential = DefaultAzureCredential()

        # Create the BlobServiceClient object
        return BlobServiceClient(account_url, credential=default_credential)

    def upload_blob(self, file, blob_name: str) -> None:
        # Create a blob client and upload new blob
        blob_client = self.get_blob_service_client().get_blob_client(container=C.TDH_UPLOAD_STORAGE_CONTAINER, blob=blob_name)
        blob_client.upload_blob(file)
        
    def download_blob_as_json(self, blob_name: str) -> Any:
        blob_client = self.get_blob_service_client().get_blob_client(container=C.TDH_UPLOAD_STORAGE_CONTAINER, blob=blob_name)
        blob_data = blob_client.download_blob().content_as_text()
        
        return json.loads(blob_data)


class BlobUploadView(MethodView):
    """Upload new blob to Azure Blob Storage"""

    def _prepare(self, id: str, resource_id: str) -> dict[str, Any]:
        # check user is authorised to upload
        user = toolkit.current_user.name
        try:
            toolkit.check_access('resource_update', {'user': user}, {'id': resource_id})
        except toolkit.NotAuthorized:
            return toolkit.abort(403, ("User %r not authorized to edit %s") % (user, id))

        try:
            # resource_edit_base template uses these
            pkg_dict = toolkit.get_action('package_show')({}, {'id': id})
            resource = toolkit.get_action('resource_show')({}, {'id': resource_id})

            return {
                'pkg_dict': pkg_dict,
                'resource': resource,
            }

        except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
            toolkit.abort(404, "Resource not found")

    def get(self, id: str, resource_id: str):
        data_dict = self._prepare(id, resource_id)

        # global variables required for package components
        toolkit.g.pkg_dict = data_dict['pkg_dict']
        toolkit.g.resource = data_dict['resource']

        return toolkit.render('package/resource_upload.html', data_dict)

    def post(self, id: str, resource_id: str):
        data_dict = self._prepare(id, resource_id)

        # create a temp directory
        with tempfile.TemporaryDirectory() as tmp:
            temp_dir = Path(tmp)

            try:
                upload_file, filename, filesize = get_request_file()
                verify_file(filename, filesize)

                # save uploaded file to temp directory
                upload_file.seek(0, os.SEEK_SET)
                upload_file.save(f"{temp_dir}/{filename}")
                upload_file.close()

                timestamp = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
                upload_body = create_signiture_body(id, resource_id, data_dict, timestamp)

                # set blob directory path
                blobdir = f"Publisher/{upload_body['publisher_title']}/{upload_body['dataset_title']}/{upload_body['resource_name']}"
                upload_body["path"] = f"{blobdir}/{timestamp}.zip"

                # generate signiture file
                generate_signiture_file(f"{temp_dir}/info.json", upload_body)

                try:
                    # zip uploaded file and signiture file
                    with zipfile.ZipFile(f"{temp_dir}/upload.zip", "w") as zipf:
                        zipf.write(f"{temp_dir}/{filename}", arcname=filename)
                        zipf.write(f"{temp_dir}/info.json", arcname="info.json")

                    # upload zip file to blob storage
                    BlobStorage().upload_blob(
                        open(f"{temp_dir}/upload.zip", "rb"), upload_body["path"]
                    )
                    call_http_trigger(upload_body)
                    flash(C.UPLOAD_STATUS_SUCCESS, category="alert-success")

                except Exception as e:
                    flash(f"{C.UPLOAD_STATUS_FAILED}: {e}", category="alert-danger")

            except Exception as e:
                flash(f"{C.UPLOAD_STATUS_FAILED}: {e}", category="alert-danger")

        return toolkit.redirect_to("upload.blob", id=id, resource_id=resource_id)


uploadbp.add_url_rule(
    "/dataset/<id>/upload_form/<resource_id>",
    view_func=BlobUploadView.as_view(str("blob")),
)
