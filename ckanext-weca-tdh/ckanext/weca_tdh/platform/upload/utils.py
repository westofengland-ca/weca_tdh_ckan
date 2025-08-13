import json
import os
from typing import Any

import ckanext.weca_tdh.config as C
from flask import request


def get_request_file() -> tuple[Any, str, int]:
    upload_file = request.files["file"]
    upload_file.seek(0, os.SEEK_END)
    filename = upload_file.filename
    filesize = upload_file.tell()

    return upload_file, filename, filesize


def verify_file(filename: str, file_size: int) -> None:
    _, ext = os.path.splitext(filename)

    if ext not in C.TDH_UPLOAD_FILE_TYPES:
        raise Exception("Unsupported file type.")
    if file_size > C.TDH_UPLOAD_FILE_SIZE:
        raise Exception("File size too large.")


def create_signature_body(id, resource_id, data_dict, timestamp) -> dict:
    return {
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


def generate_signature_file(file_path: str, body: dict) -> None:
    with open(file_path, "w") as f:
        json.dump(body, f)
