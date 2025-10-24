import logging
import os
import threading
import uuid

import ckan.plugins.toolkit as toolkit
import ckanext.weca_tdh.config as C
import requests
from ckanext.weca_tdh.platform.redis_config import RedisConfig
from flask import flash, jsonify, request, send_file

from .workspace import DatabricksWorkspace

log = logging.getLogger(__name__)
redis_client = RedisConfig(C.REDIS_URL)


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


def start_download():
    workspace = DatabricksWorkspace()
    try:
        data = request.get_json()

        resource_id = data.get("resource_id")
        if not resource_id:
            raise Exception("missing resource ID")
        
        catalog = workspace.get_catalog_files(resource_id)
        if not catalog:
            raise Exception("unable to retrieve file catalog")
        
        file_name = catalog.get('file_name')
        file_url = (
            f"https://{workspace.host}/api/2.0/fs/files/Volumes/"
            f"{catalog.get('catalog_name')}/"
            f"{catalog.get('schema_name')}/"
            f"{catalog.get('volume_name')}/"
            f"{file_name}"
        )

        output_path = os.path.join("/tmp", file_name)
        access_token = workspace.get_workspace_access_token()

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