import json
import ckanext.weca_tdh.config as C
import ckan.plugins.toolkit as toolkit

class RouteController():
    def render_contact_page():
        return toolkit.render('contact.html')
    
    def render_policy_page():
        return toolkit.render('policy.html')
    
    def render_accessibility_page():
        return toolkit.render('accessibility.html')
    
    def render_tdh_partner_connect_page():
        return toolkit.render('tdh_partner_connect.html')

    def download_tdh_partner_connect_file():
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
                "address": {
                  "host": host,
                  "path": path
                },
                "authentication": None,
                "query": None
              },
              "options": {
                "Catalog": "",
                "Database": ""
              },
              "mode": "DirectQuery"
            }
          ]
        }

        return json.dumps(file)
