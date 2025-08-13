import logging

from flask import Blueprint

databricksbp = Blueprint('databricks', __name__)
log = logging.getLogger(__name__)
