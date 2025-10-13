import base64
import hashlib
import logging
import os
import threading
import time
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
from ckanext.weca_tdh.platform.redis_config import RedisConfig
from ckanext.weca_tdh.upload import BlobStorage

log = logging.getLogger(__name__)
databricksbp = Blueprint('databricks', __name__)

# Redis config
redis_client = RedisConfig(C.REDIS_URL)


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
        redis_client.set_download_status(task_id, status="in_progress", message="Download started.")
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        with requests.get(file_url, headers=headers, stream=True) as response:
            response.raise_for_status()
            with open(output_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

        redis_client.set_download_status(task_id, status="completed", message="Download completed.", file_path=output_path)
    except requests.exceptions.HTTPError as e:
        status_code = getattr(e.response, "status_code", None)
        message = {
            400: "invalid request",
            401: "unauthorized access",
            403: "unauthorized access",
            404: "file not available",
        }.get(status_code, str(e)) 
        
        redis_client.set_download_status(task_id, status="error", message=f"Download failed: {message}. Contact the Data Owner for support.")
    except Exception as e:
        redis_client.set_download_status(task_id, status="error", message=f"Download failed: {e}.")


@databricksbp.route('/databricks/download/status', methods=['POST'])
def get_task_status():
    data = request.get_json()
    task_id = data.get("task_id")
    
    if not task_id:
        flash("Failed to get download status: Task ID is required.", category='alert-danger')
        return jsonify({"status": "error", "message": "task_id is required."}), 400
    
    task_info = redis_client.get_download_status(task_id)
    
    if task_info:
        if task_info["status"] == "error":
            redis_client.delete_download_task(task_id)
            flash(task_info["message"], category='alert-danger')
        return jsonify(task_info)
    else:
        flash("Failed to get download status: Task ID not found.", category='alert-danger')
        return jsonify({"status": "not_found", "message": "Task ID not found."}), 404


@databricksbp.route('/databricks/download/<task_id>', methods=['GET'])
def download_file(task_id):
    task_info = redis_client.get_download_status(task_id)
    
    if not task_info:
        flash("Failed to download file: Task ID not found.", category='alert-danger')
        return toolkit.redirect_to(request.referrer or "/")

    file_path = task_info["file_path"]

    if not os.path.exists(file_path):
        redis_client.delete_download_task(task_id)
        flash("Failed to download file: file not found.", category='alert-danger')
        return toolkit.redirect_to(request.referrer or "/")

    filename = os.path.basename(file_path)
    
    try:
        return send_file(file_path, as_attachment=True, download_name=filename)
    finally:
        try:
            redis_client.delete_download_task(task_id)
            os.remove(file_path) # Remove temporary file
        except Exception as e:
            log.error(f"Error deleting file {file_path}: {e}")


class DatabricksWorkspace(object):
    def __init__(self):
        self.host = C.TDH_CONNECT_ADDRESS_HOST
        self.warehouse_id = str(C.TDH_CONNECT_ADDRESS_PATH).split('/')[-1]
        
    @property
    def user_id(self):
        return toolkit.current_user.id if toolkit.current_user else "anon"
    
    def set_tokens(self, access_token, refresh_token, expires_at, refresh_expires_at):
        redis_client.set_databricks_tokens(self.user_id, access_token, refresh_token, expires_at, refresh_expires_at)

    def get_tokens(self):
        return redis_client.get_databricks_tokens(self.user_id)

    def delete_tokens(self):
        redis_client.delete_databricks_tokens(self.user_id)
    
    def authenticate(self, resource_id):
        referrer = request.args.get("referrer", "/dataset")
        code_verifier, code_challenge = oauth_code_verify_and_challenge()

        session['databricks'] = {
            "code_verifier": code_verifier,
            "referrer": referrer,
            "resource_id": resource_id
        }

        # Redirect to OAuth
        auth_url = self.build_databricks_auth_url(code_challenge, resource_id)
        return toolkit.redirect_to(auth_url)
    
    @staticmethod
    def build_databricks_auth_url(code_challenge: str, resource_id: str) -> str:
        client_id = C.TDH_DB_APP_CLIENT_ID
        redirect_url = C.TDH_DB_APP_REDIRECT_URL

        return (
            f"https://{C.TDH_CONNECT_ADDRESS_HOST}/oidc/v1/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_url}"
            f"&response_type=code"
            f"&state={resource_id}"
            f"&code_challenge={code_challenge}"
            f"&code_challenge_method=S256"
            f"&scope=all-apis+offline_access"
        )
        
    def authorise(self):
        try:
            referrer = session.get('databricks', {}).get('referrer', '/')
            resource_id = session.get('databricks', {}).get('resource_id')

            auth_code = self.get_workspace_auth_code()
            code_verifier = session.get('databricks', {}).get('code_verifier')

            response_dict = self.generate_workspace_access_token(code_verifier, auth_code)
            
            access_token = response_dict.get("access_token")
            refresh_token = response_dict.get("refresh_token")

            now = time.time()
            expires_at = int(now) + int(response_dict.get("expires_in", 3600))
            refresh_expires_at = int(now) + 604800 # 7 days

            self.set_tokens(access_token, refresh_token, expires_at, refresh_expires_at)
            session.pop('databricks', None)

            if resource_id:
                sep = "&" if "?" in referrer else "?"
                referrer = f"{referrer}{sep}autodownload={resource_id}"

            return toolkit.redirect_to(referrer)

        except Exception as e:
            flash(f"Download authorisation failed: {e}.", category='alert-danger')
            return toolkit.redirect_to(referrer)

    @staticmethod
    def get_workspace_auth_code() -> str:  
        return request.args.get('code')

    def generate_workspace_access_token(self, code_verifier: str, auth_code: str) -> str:
        base_url = f"https://{self.host}/oidc/v1/token"
        client_id = C.TDH_DB_APP_CLIENT_ID
        redirect_url = C.TDH_DB_APP_REDIRECT_URL

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
            return response_dict
        except Exception:
            raise Exception('invalid access token')
        
    def get_workspace_access_token(self) -> str:
        token_data = self.get_tokens()

        if not token_data:
            raise Exception("Databricks session expired. Please log in again")

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_at = int(token_data.get("expires_at", 0))
        refresh_expires_at = int(token_data.get("refresh_expires_at", 0))
        
        now = time.time()

        # Refresh access token if expired
        if now > expires_at:
            if not refresh_token or now > refresh_expires_at:
                self.delete_tokens()
                raise Exception("Databricks session expired. Please log in again")

            access_token = self.refresh_workspace_access_token(refresh_token, refresh_expires_at)

        return access_token

    def refresh_workspace_access_token(self, refresh_token: str, refresh_expires_at: int) -> int:
        base_url = f"https://{self.host}/oidc/v1/token"
        client_id = C.TDH_DB_APP_CLIENT_ID

        data = {
            "client_id": client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        response = requests.post(base_url, data=data)
        response_dict = response.json()

        if "access_token" not in response_dict:
            self.delete_tokens()
            raise Exception("Failed to refresh Databricks session. Please log in again")

        access_token = response_dict["access_token"]
        expires_at = int(time.time()) + int(response_dict.get("expires_in", 3600))
        
        self.set_tokens(access_token, refresh_token, expires_at, refresh_expires_at)

        return access_token
        
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

            output_path = os.path.join("/tmp", file_name)
            access_token = self.get_workspace_access_token()

            task_id = str(uuid.uuid4()) # Generate unique task ID
            redis_client.set_download_status(task_id, status="pending", message="Task started.")
             
            thread = threading.Thread(target=download_file_from_url, args=(task_id, file_url, output_path, access_token))
            thread.daemon = True
            thread.start()

            download_url = f"/databricks/download/{task_id}"
            return jsonify({"task_id": task_id, "download_url": download_url, "message": "Download started."})
        except Exception as e:
            error_message = f"Download failed to start: {e}."
            flash(error_message, category='alert-danger')
            return jsonify({"status": "error", "message": error_message}), 500
            
    @staticmethod
    def get_catalog_files(resource_id):
        json_data = BlobStorage().download_blob_as_json('databricks.json')
        catalog_files = json_data.get("catalog_files", {})
        return catalog_files.get(resource_id, None)


databricksbp.add_url_rule('/databricks/auth/initiate/<resource_id>', 
                          view_func=DatabricksWorkspace().authenticate)
databricksbp.add_url_rule('/databricks/auth', 
                          view_func=DatabricksWorkspace().authorise)
databricksbp.add_url_rule('/databricks/download/start', 
                          view_func=DatabricksWorkspace().start_download, methods=['POST'])
