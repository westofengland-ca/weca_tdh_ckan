from flask import Blueprint

from .auth import authenticate, authorise
from .download import download_file, get_task_status, start_download

databricksbp = Blueprint('databricks', __name__)


databricksbp.add_url_rule('/databricks/auth/initiate/<resource_id>', 
                          view_func=authenticate)
databricksbp.add_url_rule('/databricks/auth', 
                          view_func=authorise)
databricksbp.add_url_rule('/databricks/download/start', 
                          view_func=start_download, methods=['POST'])
databricksbp.add_url_rule('/databricks/download/<task_id>', 
                          view_func=download_file, methods=['GET'])
databricksbp.add_url_rule('/databricks/download/status', 
                          view_func=get_task_status, methods=['POST'])
