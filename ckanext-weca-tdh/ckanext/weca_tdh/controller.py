import json

import ckan.plugins.toolkit as toolkit

import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.lib.helpers import update_package_metadata_list


class RouteController(object):
    """Manage static page routing"""
    
    @staticmethod
    def render_support_page():
        return toolkit.render('/support/support.html')
    
    @staticmethod
    def render_support_pages(path=None):
        if not path:
            return toolkit.render('/support/support.html')
        return toolkit.render(f'/support/{path}.html')
    
    @staticmethod
    def render_tdh_partner_connect_page():
        return toolkit.render('tdh_partner_connect.html')
    
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
