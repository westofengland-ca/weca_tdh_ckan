import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

import ckan.plugins.toolkit as toolkit
import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.platform.upload.blob_storage import BlobStorage
from ckanext.weca_tdh.platform.upload.http_trigger import call_http_trigger
from ckanext.weca_tdh.platform.upload.utils import (
    create_signature_body,
    generate_signature_file,
    get_request_file,
    verify_file,
)
from flask import flash


def _prepare_upload(id: str, resource_id: str) -> dict[str, Any]:
    user = toolkit.current_user.name
    try:
        toolkit.check_access('resource_update', {'user': user}, {'id': resource_id})
    except toolkit.NotAuthorized:
        return toolkit.abort(403, ("User %r not authorized to edit %s") % (user, id))

    try:
        pkg_dict = toolkit.get_action('package_show')({}, {'id': id})
        resource = toolkit.get_action('resource_show')({}, {'id': resource_id})
        return {'pkg_dict': pkg_dict, 'resource': resource}
    except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
        toolkit.abort(404, "Resource not found")


def handle_upload_get(id: str, resource_id: str):
    data_dict = _prepare_upload(id, resource_id)
    toolkit.g.pkg_dict = data_dict['pkg_dict']
    toolkit.g.resource = data_dict['resource']

    return toolkit.render('package/resource_upload.html', data_dict)


def handle_upload_post(id: str, resource_id: str):
    data_dict = _prepare_upload(id, resource_id)

    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)

        try:
            upload_file, filename, filesize = get_request_file()
            verify_file(filename, filesize)

            upload_file.seek(0)
            upload_file.save(f"{temp_dir}/{filename}")
            upload_file.close()

            timestamp = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
            upload_body = create_signature_body(id, resource_id, data_dict, timestamp)

            blobdir = f"Publisher/{upload_body['publisher_title']}/{upload_body['dataset_title']}/{upload_body['resource_name']}"
            upload_body["path"] = f"{blobdir}/{timestamp}.zip"

            generate_signature_file(f"{temp_dir}/info.json", upload_body)

            with zipfile.ZipFile(f"{temp_dir}/upload.zip", "w") as zipf:
                zipf.write(f"{temp_dir}/{filename}", arcname=filename)
                zipf.write(f"{temp_dir}/info.json", arcname="info.json")

            BlobStorage().upload_blob( open(f"{temp_dir}/upload.zip", "rb"), upload_body["path"])
            call_http_trigger(upload_body)

            flash(C.UPLOAD_STATUS_SUCCESS, category="alert-success")
        except Exception as e:
            flash(f"{C.UPLOAD_STATUS_FAILED}: {e}", category="alert-danger")

    return toolkit.redirect_to("upload.blob", id=id, resource_id=resource_id)
