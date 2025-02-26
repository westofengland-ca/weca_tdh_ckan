import json

import ckan.plugins.toolkit as toolkit

import ckanext.weca_tdh.config as C


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
