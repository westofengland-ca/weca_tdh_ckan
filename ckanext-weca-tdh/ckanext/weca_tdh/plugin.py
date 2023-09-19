from ckan.common import CKANConfig, session
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model
import ckan.lib.helpers as h
from flask import Blueprint, render_template
from inspect import getmembers, isfunction
from ckanext.weca_tdh.lib import helpers
import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.controller import RouteController
from ckanext.weca_tdh.auth import ADAuth

def login_aad_redirect():
    if not session.get('user'):
        return h.redirect_to('auth.login')
    return render_template('home/index.html')

def logout_aad_redirect():
    return h.redirect_to('/')

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
        if session.get('user'):
            user = model.User.get(session.get('user'))
            toolkit.login_user(user)
    
    def login(self):
        pass
    
    def logout(self):
        """
        Called on logout.
        """
        session.clear()
        toolkit.logout_user()
        return h.redirect_to(C.CKAN_ROUTE_AD_LOGOUT)

    def get_blueprint(self):      
        '''
        Creates a flask blueprint with specified url rules to allow static page routing
        '''       
        staticbp = Blueprint(self.name, self.__module__, template_folder='templates')
        rules = [
            ('/', 'index', login_aad_redirect)
            ('/user/logged_out_redirect', 'logout', logout_aad_redirect)
            ('/contact', 'contact', RouteController.render_contact_page),
            ('/policy', 'policy', RouteController.render_policy_page),
            ('/license', 'license', RouteController.render_license_page)
        ]
        for rule in rules:
            staticbp.add_url_rule(*rule)

        return [staticbp, ADAuth.get_blueprint()]
