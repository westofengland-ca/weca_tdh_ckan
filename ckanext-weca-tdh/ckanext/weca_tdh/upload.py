import json, logging, os, requests, tempfile, zipfile
from datetime import datetime
from typing import Any
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import ckan.plugins.toolkit as toolkit
from flask import Blueprint, flash, request
from flask.views import MethodView
import ckanext.weca_tdh.config as C
from pathlib import Path

log = logging.getLogger(__name__)
uploadbp = Blueprint('upload', __name__)


class Upload(object):

    def verify_file(filename: str, file_size: int) -> None:
        # get file extension
        _, ext = os.path.splitext(filename)

        if ext not in C.TDH_UPLOAD_FILE_TYPES:
            raise Exception("Unsupported file type.")

        if file_size > C.TDH_UPLOAD_FILE_SIZE:
            raise Exception("File size too large.")
        
    @staticmethod
    def generate_signiture_file(file_path: str, body: dict) -> None:
        with open(file_path, 'w') as file:
            json.dump(body, file)

    @staticmethod
    def call_http_trigger(body: dict) -> None:
        url = C.TDH_UPLOAD_HTTP_TRIGGER
        response = requests.post(url, json=body)

        if not response.ok:
            raise Exception(f"HTTP trigger status code {response.status_code}")

class BlobStorage():

    @staticmethod
    def get_blob_service_client():
        account_url = f"https://{C.TDH_UPLOAD_STORAGE_ACCOUNT}.blob.core.windows.net"
        default_credential = DefaultAzureCredential()

        # Create the BlobServiceClient object
        return BlobServiceClient(account_url, credential=default_credential)

    def upload_blob(self, file, filename: str) -> None:
        # Create a blob client and upload new blob
        blob_client = self.get_blob_service_client().get_blob_client(container=C.TDH_UPLOAD_STORAGE_CONTAINER, blob=filename)
        blob_client.upload_blob(file)

class BlobUploadView(MethodView):
    
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
                upload_file = request.files['file']
                upload_file.seek(0, os.SEEK_END)
                filename = upload_file.filename
                filesize = upload_file.tell()

                # check file type and size
                Upload.verify_file(filename, filesize)

                # save uploaded file to temp directory
                upload_file.seek(0, os.SEEK_SET)
                upload_file.save(f"{temp_dir}/{filename}")
                upload_file.close()

                timestamp = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")

                # get upload info
                upload_info = {
                    'upload_date': timestamp,
                    'author': request.form['author'],
                    'author_email': request.form['author_email'],
                    'description': request.form['desc'],
                    'resource_id': resource_id,
                    'resource_name': data_dict['resource']['name'],
                    'dataset_id': data_dict['resource']['package_id'],
                    'dataset_name': id,
                    'dataset_title': data_dict['pkg_dict']['title'],
                    'publisher_id': data_dict['pkg_dict']['organization']['id'],
                    'publisher_name': data_dict['pkg_dict']['organization']['name'],
                    'publisher_title': data_dict['pkg_dict']['organization']['title']
                }

                # set blob directory path
                blobdir = f"Publisher/{upload_info['publisher_title']}/{upload_info['dataset_title']}/{upload_info['resource_name']}"
                upload_info['path'] = f"{blobdir}/{timestamp}.zip"

                # generate signiture file
                Upload.generate_signiture_file(f"{temp_dir}/info.json", upload_info)

                try:
                    # zip uploaded file and signiture file
                    with zipfile.ZipFile(f"{temp_dir}/upload.zip", 'w') as zipf:
                        zipf.write(f"{temp_dir}/{filename}", arcname=filename)
                        zipf.write(f"{temp_dir}/info.json", arcname="info.json")

                    # upload zip file to blob storage
                    BlobStorage.upload_blob(open(f"{temp_dir}/upload.zip", "rb"), upload_info['path'])
                    Upload.call_http_trigger(upload_info)
                    flash(C.UPLOAD_STATUS_SUCCESS, category='alert-success')

                except Exception as e:
                    flash(f'{C.UPLOAD_STATUS_FAILED}: {e}', category='alert-danger')

            except Exception as e:
                flash(f'{C.UPLOAD_STATUS_FAILED}: {e}', category='alert-danger')

        return toolkit.redirect_to('upload.blob', id=id, resource_id=resource_id)

uploadbp.add_url_rule('/dataset/<id>/upload_form/<resource_id>', view_func=BlobUploadView.as_view(str('blob')))
