import base64
import hashlib
import json
import logging
import os
import threading
import uuid

import ckan.plugins.toolkit as toolkit
import requests
from flask import (
    Blueprint,
    flash,
    jsonify,
    request,
    send_file,
    session,
)

import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.upload import BlobStorage

log = logging.getLogger(__name__)
databricksbp = Blueprint('databricks', __name__)
task_statuses = {}
download_directory = "/tmp"


def oauth_code_verify_and_challenge() -> tuple[str, str]:
    uuid1 = uuid.uuid4()
    uuid_str1 = str(uuid1).upper()
    
    code_verifier = uuid_str1 + "-" + uuid_str1
    
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')
    
    return code_verifier, code_challenge


def download_file_from_url(task_id, file_url, output_path, access_token):
    try:
        task_statuses[task_id] = {"status": "in_progress", "message": "Download started."}
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        with requests.get(file_url, headers=headers, stream=True) as response:
            response.raise_for_status()
            with open(output_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

        task_statuses[task_id] = {"status": "completed", "message": "Download completed.", "file_path": output_path}
    except requests.exceptions.HTTPError as e:
        status_code = getattr(e.response, "status_code", None)
        message = {
            400: "invalid request",
            401: "unauthorized access",
            403: "unauthorized access",
            404: "file not available",
        }.get(status_code, str(e)) 
        
        task_statuses[task_id] = {"status": "error", "message": f"Download failed: {message}. Contact the Data Owner for suport."}
    except Exception as e:
        task_statuses[task_id] = {"status": "error", "message": f"Download failed: {e}"}


@databricksbp.route('/databricks/download/status', methods=['POST'])
def get_task_status():
    data = request.get_json()
    task_id = data.get("task_id")
    
    if not task_id:
        flash("Failed to get download status: Task ID is required.", category='alert-danger')
        return jsonify({"status": "error", "message": "task_id is required."}), 400

    if task_id in task_statuses:
        task_info = task_statuses[task_id]
        if task_info["status"] == "error":
            flash(task_info["message"], category='alert-danger') 
        return jsonify(task_statuses[task_id])
    else:
        flash("Failed to get download status: Task ID not found.", category='alert-danger')
        return jsonify({"status": "not_found", "message": "Task ID not found."}), 404


@databricksbp.route('/databricks/download/<task_id>', methods=['GET'])
def download_file(task_id):
    if task_id not in task_statuses:
        flash("Failed to download file: Task ID not found.", category='alert-danger')
        return toolkit.redirect_to(request.referrer or "/")

    task_info = task_statuses[task_id]
    file_path = task_info["file_path"]

    if not os.path.exists(file_path):
        flash("Failed to download file: file not found.", category='alert-danger')
        return toolkit.redirect_to(request.referrer or "/")

    filename = os.path.basename(file_path)
    
    try:
        return send_file(file_path, as_attachment=True, download_name=filename)
    finally:
        try:
            # Remove temporary file
            os.remove(file_path)
            del task_statuses[task_id]
        except Exception as e:
            log.error(f"Error deleting file {file_path}: {e}")


class DatabricksWorkspace(object):
    def __init__(self):
        self.host = C.TDH_CONNECT_ADDRESS_HOST
        self.warehouse_id = str(C.TDH_CONNECT_ADDRESS_PATH).split('/')[-1]
        
    def authorise(self):
        try:
            referrer = session.get('referrer', '/')
            
            # Get workspace authorisation code for user
            auth_code = self.get_workspace_auth_code()
            
            # Get auth code verifier
            code_verifier = session.get('code_verifier')
            
            # Get/set workspace access token for user
            access_token = self.generate_workspace_access_token(code_verifier, auth_code)
            session['access_token'] = access_token
            
            # Redirect back to resource page
            return toolkit.redirect_to(referrer)

        except Exception as e:
            flash(f"Download authorisation failed: {e}. Contact the Data Owner for support.", category='alert-danger')
            return toolkit.redirect_to(referrer)

    @staticmethod
    def get_workspace_auth_code() -> str:  
        return request.args.get('code')
    
    @staticmethod
    def get_workspace_access_token() -> str:
        return session.get('access_token')

    def generate_workspace_access_token(self, code_verifier: str, auth_code: str) -> str:
        base_url = f"https://{self.host}/oidc/v1/token"
        client_id = C.DB_APP_CLIENT_ID
        redirect_url = C.DB_APP_REDIRECT_URL

        data = {
            "client_id": client_id,
            "grant_type": "authorization_code",
            "scope": "all-apis offline_access",
            "redirect_uri": redirect_url,
            "code_verifier": code_verifier,
            "code": auth_code
        }

        try:
            response = requests.post(base_url, data=data)
            response_dict = response.json()
            return response_dict.get("access_token")
        except Exception:
            raise Exception('invalid access token')
        
    def start_download(self):
        try:
            data = request.get_json()

            resource_id = data.get("resource_id")
            if not resource_id:
                raise Exception("missing resource ID")
            
            catalog = self.get_catalog_files(resource_id)
            if not catalog:
                raise Exception("unable to retrieve file catalog")
            
            file_name = catalog.get('file_name')
            file_url = (
                f"https://{self.host}/api/2.0/fs/files/Volumes/"
                f"{catalog.get('catalog_name')}/"
                f"{catalog.get('schema_name')}/"
                f"{catalog.get('volume_name')}/"
                f"{file_name}"
            )

            output_path = os.path.join(download_directory, file_name)
            access_token = self.get_workspace_access_token()

            task_id = str(uuid.uuid4()) # Generate unique task ID
            thread = threading.Thread(target=download_file_from_url, args=(task_id, file_url, output_path, access_token))
            thread.daemon = True
            thread.start()

            download_url = f"/databricks/download/{task_id}"
            return jsonify({"task_id": task_id, "download_url": download_url, "message": "Download started."})
        except Exception as e:
            error_message = f"Download failed to start: {e}. Contact the Data Owner for support."
            flash(error_message, category='alert-danger')
            return jsonify({"status": "error", "message": error_message}), 500
            
    @staticmethod
    def get_catalog_files(resource_id):
        json_data = BlobStorage().download_blob_as_json('databricks.json')
        catalog_files = json_data.get("catalog_files", {})

        return catalog_files.get(resource_id, None)


databricksbp.add_url_rule('/databricks/auth', 
                          view_func=DatabricksWorkspace().authorise)
databricksbp.add_url_rule('/databricks/download/start', 
                          view_func=DatabricksWorkspace().start_download, methods=['POST'])
