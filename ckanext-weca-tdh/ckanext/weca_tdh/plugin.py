from ckan.common import CKANConfig
import ckan.lib.helpers as h
from ckan.model.user import AnonymousUser
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.types import Context, Schema
from flask import Blueprint, flash, request
from inspect import getmembers, isfunction
from ckanext.weca_tdh.auth import adauthbp
import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.controller import RouteController
from ckanext.weca_tdh.lib import helpers
from typing import Any
import logging

log = logging.getLogger(__name__)

class WecaTdhPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IAuthenticator, inherit=True)
    plugins.implements(plugins.IBlueprint, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer
    def update_config(self, config: CKANConfig):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "public")
        toolkit.add_resource("assets", "weca_tdh")

    def get_helpers(self):       
        '''
        Returns a dict of extra weca-tdh specific helper functions to be used in a template
        '''
        helper_dict = {}

        functions_list = [f for f in getmembers(helpers, isfunction)]
        for name, fn in functions_list:
            helper_dict[name] = fn

        return helper_dict

    def identify(self):
        """
        Called on each request to identify a user.
        """
        if C.FF_AUTH_RESTRICTED_ACCESS == 'True' and not any(subpath in request.path for subpath in C.EXLUDED_SUBPATHS):         
            if isinstance(toolkit.current_user, AnonymousUser): # check for an unauthorised user
                flash(C.ALERT_MESSAGE_AUTH, category='alert-info')
                return toolkit.render('/user/login.html') # redirect to login page with flash message

    def login(self):
        pass
    
    def logout(self):
        """
        Called on logout.
        """
        toolkit.logout_user()

        # if user logged in using AD, log out of AD
        if C.AD_SESSION_COOKIE in request.cookies:
            return h.redirect_to(C.CKAN_ROUTE_AD_LOGOUT)

    def get_blueprint(self):      
        '''
        Creates a flask blueprint with specified url rules to allow static page routing
        '''       
        staticbp = Blueprint(self.name, self.__module__, template_folder='templates')
        rules = [
            ('/contact', 'contact', RouteController.render_contact_page),
            ('/policy', 'policy', RouteController.render_policy_page),
            ('/accessibility', 'accessibility', RouteController.render_accessibility_page),
            ('/tdh_partner_connect', 'tdh_partner_connect', RouteController.render_tdh_partner_connect_page),
            ('/tdh_partner_connect_file', 'tdh_partner_connect_file', RouteController.download_tdh_partner_connect_file)
        ]
        for rule in rules:
            staticbp.add_url_rule(*rule)

        return [staticbp, adauthbp]

    ''' 
    Modify dataset metadata fields
    '''  
    def _modify_package_schema(self, schema: Schema) -> Schema:
        # modify package schema with custom field
        schema.update({
            'datalake_active': [toolkit.get_validator('ignore_missing'),
                                toolkit.get_validator('boolean_validator'),
                                toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def create_package_schema(self) -> Schema:
        # get default package schema
        schema: Schema = super(WecaTdhPlugin, self).create_package_schema()
        return self._modify_package_schema(schema)

    def update_package_schema(self) -> Schema:
        schema: Schema = super(WecaTdhPlugin, self).update_package_schema()
        return self._modify_package_schema(schema)

    def show_package_schema(self) -> Schema:
        schema: Schema = super(WecaTdhPlugin, self).show_package_schema()
        schema.update({
            'datalake_active': [toolkit.get_converter('convert_from_extras'),
                                toolkit.get_validator('ignore_missing'),
                                toolkit.get_validator('boolean_validator')]
        })
        return schema
    
    def setup_template_variables(self, context: Context, data_dict: dict[str, Any]) -> Any:
        return super(WecaTdhPlugin, self).setup_template_variables(context, data_dict)
    
    def package_form(self) -> Any:
        return super(WecaTdhPlugin, self).package_form()
    
    def is_fallback(self):
        return True

    def package_types(self) -> list[str]:
        return []
