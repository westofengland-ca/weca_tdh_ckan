from ckan.common import CKANConfig
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint
from ckanext.weca_tdh.controller import RouteController

class WecaTdhPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint, inherit=True)
    
    # IConfigurer
    def update_config(self, config: CKANConfig):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "public")
        toolkit.add_resource("assets", "weca_tdh")

    def get_helpers(self):       
        '''
        Returns a dict of extra weca-tdh specific helper functions to be used in a template
        '''
        from ckanext.weca_tdh.lib import helpers
        from inspect import getmembers, isfunction

        helper_dict = {}

        functions_list = [f for f in getmembers(helpers, isfunction)]
        for name, fn in functions_list:
            helper_dict[name] = fn

        return helper_dict
    
    def get_blueprint(self):      
        '''
        Creates a flask blueprint with specified url rules to allow custom page routing
        '''       
        blueprint = Blueprint(self.name, self.__module__, template_folder='templates')
        rules = [
            ('/contact', 'contact', RouteController.render_contact_page),
            ('/policy', 'policy', RouteController.render_policy_page),
            ('/license', 'license', RouteController.render_license_page)
        ]
        for rule in rules:
            blueprint.add_url_rule(*rule)

        return blueprint
