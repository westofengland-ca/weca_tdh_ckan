import csv
import json
import logging
import os
import threading
import time
import uuid
from pathlib import Path

import ckan.plugins.toolkit as toolkit
import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.platform.redis_config import RedisConfig
from flask import flash, jsonify, request, send_file

from .workspace import DatabricksWorkspace

log = logging.getLogger(__name__)
redis_client = RedisConfig(C.REDIS_URL)
#workspace = DatabricksWorkspace()


class QueryLoader:
    def __init__(self, json_path: str):
        self.json_path = Path(json_path)
        self._queries = None

    def _load_json(self):
        if not self.json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {self.json_path}")
        with open(self.json_path, "r") as f:
            self._queries = json.load(f)

    def get_queries_for_resource(self, resource_id: str):
        if self._queries is None:
            self._load_json()
        return self._queries.get(resource_id, [])


def download_file_from_query(task_id, stmt, output_path):
    try:
        redis_client.set_download_status(task_id, status="in_progress", message="Query running...")

        columns = stmt.manifest.schema.columns
        column_names = [col.name for col in columns]
        data = stmt.result.data_array

        with open(output_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(column_names)
            writer.writerows(data)

        redis_client.set_download_status(
            task_id,
            status="completed",
            message="Query results ready for download.",
            file_path=output_path
        )
    except Exception as e:
        redis_client.set_download_status(task_id, status="error", message=f"Query failed: {e}")


def start_query_download():
    workspace = DatabricksWorkspace()
    try:
        data = request.get_json()
        task_id = str(uuid.uuid4())
        tdh_table = data.get("tdh_table", task_id)
        sql_query = data.get("sql_query")

        if not sql_query:
            raise Exception("missing SQL query")
        
        workspace_client = workspace.get_workspace_client()
        stmt = workspace.execute_statement(workspace_client, sql_query)
        
        ext = "csv"
        output_path = os.path.join("/tmp", tdh_table + os.extsep + ext)

        redis_client.set_download_status(task_id, status="pending", message="Task started.")

        thread = threading.Thread(target=download_file_from_query, args=(task_id, stmt, output_path))
        thread.daemon = True
        thread.start()

        download_url = f"/databricks/query/download/{task_id}"
        return jsonify({"task_id": task_id, "download_url": download_url, "message": "Query execution started."})
    except Exception as e:
        error_message = f"Query download failed to start: {e}."
        flash(error_message, category='alert-danger')
        return jsonify({"status": "error", "message": error_message}), 500


def get_query_task_status():
    data = request.get_json()
    task_id = data.get("task_id")

    if not task_id:
        return jsonify({"status": "error", "message": "Missing task_id"}), 400

    task_info = redis_client.get_download_status(task_id)
    if not task_info:
        return jsonify({"status": "not_found", "message": "Task ID not found."}), 404

    return jsonify(task_info)


def download_query_file(task_id):
    task_info = redis_client.get_download_status(task_id)

    if not task_info:
        flash("Failed to download query file: Task ID not found.", category='alert-danger')
        return toolkit.redirect_to(request.referrer or "/")

    file_path = task_info.get("file_path")

    if not os.path.exists(file_path):
        redis_client.delete_download_task(task_id)
        flash("Failed to download query file: file not found.", category='alert-danger')
        return toolkit.redirect_to(request.referrer or "/")

    filename = os.path.basename(file_path)

    try:
        return send_file(file_path, as_attachment=True, download_name=filename)
    finally:
        try:
            redis_client.delete_download_task(task_id)
            os.remove(file_path)
        except Exception as e:
            log.error(f"Error deleting file {file_path}: {e}")
