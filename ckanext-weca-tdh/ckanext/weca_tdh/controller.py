import json

import ckan.plugins.toolkit as toolkit
from flask import Blueprint

import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.lib.helpers import update_package_metadata_list

actionbp = Blueprint('action', __name__)


class Controller(object):
    @staticmethod
    def update_dataset_interest(dataset_id):
        pkg_dict = toolkit.get_action('package_show')({}, {'id': dataset_id})
        user_email = toolkit.g.userobj.email

        update_package_metadata_list(pkg_dict, key='expressed_interest', value=user_email)

        return toolkit.redirect_to('dataset.read', id=dataset_id)
    
    @staticmethod
    def download_tdh_partner_connect_file() -> str:
        # get config values
        host = C.TDH_CONNECT_ADDRESS_HOST
        path = C.TDH_CONNECT_ADDRESS_PATH

        # create partner connect file
        file = {
            "version": "0.1",
            "connections": [
                {
                    "details": {
                        "protocol": "databricks-sql",
                        "address": {"host": host, "path": path},
                        "authentication": None,
                        "query": None,
                    },
                    "options": {"Catalog": "", "Database": ""},
                    "mode": "DirectQuery",
                }
            ],
        }

        return json.dumps(file)

actionbp.add_url_rule('/dataset/<dataset_id>/interest', 'dataset_interest',
                          view_func=Controller.update_dataset_interest)
actionbp.add_url_rule('/tdh_partner_connect_file', 'tdh_partner_connect_file', 
                          view_func=Controller.download_tdh_partner_connect_file)
