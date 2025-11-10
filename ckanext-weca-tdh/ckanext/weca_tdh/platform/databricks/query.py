import csv
import json
import logging
import os
import re
import threading
import uuid

import ckan.plugins.toolkit as toolkit
import ckanext.weca_tdh.config as C
import pandas as pd
from ckanext.weca_tdh.platform.redis_config import RedisConfig
from flask import flash, jsonify, request, send_file
from slugify import slugify

from .workspace import DatabricksWorkspace

log = logging.getLogger(__name__)
redis_client = RedisConfig(C.REDIS_URL)


def get_resource_query(resource_id: str, query_id: int) -> str:
    """Return resource sql query for given query id."""
    if resource_id is None or query_id is None:
        raise toolkit.ValidationError("resource_id and query_index are required")

    try:
        res_dict = toolkit.get_action('resource_show')(None, {'id': resource_id})
        queries_str = res_dict.get('resource_queries')
        
        queries = json.loads(queries_str)
        
        return queries[query_id]
    except Exception as e:
        log.warning(f"Failed to get resource queries for {resource_id}: {e}")
        return ""


def download_file_from_query(task_id, stmt, query_output, output_path):
    try:
        redis_client.set_download_status(task_id, status="in_progress", message="Query running...")

        columns = stmt.manifest.schema.columns
        column_names = [col.name for col in columns]
        data = stmt.result.data_array
        
        if query_output.lower() =="json":
            rows = [dict(zip(column_names, row)) for row in data]
            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(rows, file, indent=2)
                
        elif query_output.lower() == "parquet":
            df = pd.DataFrame(data, columns=column_names)
            df.to_parquet(output_path, index=False)

        else:
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
        resource_id = data.get("resource_id")
        query_id = int(data.get("query_id"))
        format = data.get("format")

        query = get_resource_query(resource_id, query_id)
        
        if not query:
            raise Exception("missing resource query")
        
        task_id = str(uuid.uuid4())
        query_title = query.get('title') or task_id
        query_output = format if format in query.get('formats') else "csv"
        query_statement = query.get('statement')
        statement = re.sub(r'\s+', ' ', query_statement.strip())
        
        workspace_client = workspace.get_workspace_client()
        stmt = workspace.execute_statement(workspace_client, statement)
        
        file_name = slugify(query_title, separator="_")
        output_path = os.path.join("/tmp", file_name + os.extsep + query_output)

        redis_client.set_download_status(task_id, status="pending", message="Task started.")

        thread = threading.Thread(target=download_file_from_query, args=(task_id, stmt, query_output, output_path))
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
