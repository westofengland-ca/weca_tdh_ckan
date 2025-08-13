import logging

from ckanext.weca_tdh.platform.upload.logic import handle_upload_get, handle_upload_post
from flask import Blueprint
from flask.views import MethodView

log = logging.getLogger(__name__)
uploadbp = Blueprint("upload", __name__)


class BlobUploadView(MethodView):

    def get(self, id, resource_id):
        return handle_upload_get(id, resource_id)

    def post(self, id, resource_id):
        return handle_upload_post(id, resource_id)


uploadbp.add_url_rule(
    "/dataset/<id>/upload_form/<resource_id>",
    view_func=BlobUploadView.as_view(str("blob")),
)
