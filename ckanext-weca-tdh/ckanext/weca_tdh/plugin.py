from ckan.common import CKANConfig
import ckan.lib.helpers as h
from ckan.model.user import AnonymousUser
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint, flash, request
from inspect import getmembers, isfunction
from ckanext.weca_tdh.auth import adauthbp
import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.controller import RouteController
from ckanext.weca_tdh.lib import helpers
import logging

log = logging.getLogger(__name__)

class WecaTdhPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint, inherit=True)
    plugins.implements(plugins.IAuthenticator, inherit=True)

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
            ('/license', 'license', RouteController.render_license_page),
            ('/tdh_partner_connect', 'tdh_partner_connect', RouteController.render_tdh_partner_connect_page),
            ('/tdh_partner_connect_file', 'tdh_partner_connect_file', RouteController.download_tdh_partner_connect_file)
        ]
        for rule in rules:
            staticbp.add_url_rule(*rule)

        return [staticbp, adauthbp]
