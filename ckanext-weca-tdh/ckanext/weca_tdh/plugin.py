import json
import logging
import re
from inspect import getmembers, isfunction
from typing import Any

import ckan.lib.helpers as h
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import CKANConfig
from ckan.model.user import AnonymousUser
from ckan.types import Context, Schema
from flask import Blueprint, flash, request

import ckanext.weca_tdh.config as C
from ckanext.pages.interfaces import IPagesSchema
from ckanext.weca_tdh.auth import adauthbp
from ckanext.weca_tdh.controller import RouteController
from ckanext.weca_tdh.databricks import databricksbp
from ckanext.weca_tdh.lib import helpers
from ckanext.weca_tdh.upload import uploadbp

log = logging.getLogger(__name__)


class WecaTdhPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IAuthenticator, inherit=True)
    plugins.implements(plugins.IBlueprint, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IPackageController)
    plugins.implements(IPagesSchema)
    plugins.implements(plugins.IFacets)

    # IConfigurer
    def update_config(self, config: CKANConfig):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "public")
        toolkit.add_resource("assets", "weca_tdh")

    def get_helpers(self) -> dict:       
        '''
        Returns a dict of extra weca-tdh specific helper functions to be used in a template
        '''
        helper_dict = {}

        functions_list = [f for f in getmembers(helpers, isfunction)]
        for name, fn in functions_list:
            helper_dict[name] = fn

        return helper_dict

    def identify(self) -> None:
        """
        Called on each request to identify a user.
        """
        if C.FF_AUTH_RESTRICTED_ACCESS == 'True' and request.path != '/' and not any(subpath in request.path for subpath in C.EXLUDED_SUBPATHS):
            if isinstance(toolkit.current_user, AnonymousUser): # check for an unauthorised user
                flash(C.ALERT_MESSAGE_AUTH, category='alert-info')
                return toolkit.render('/user/login.html') # redirect to login page with flash message

    def login(self) -> None:
        pass
    
    def logout(self) -> None:
        """
        Called on logout.
        """
        toolkit.logout_user()

        # if user logged in using AD, log out of AD
        if C.AD_SESSION_COOKIE in request.cookies:
            return h.redirect_to(C.CKAN_ROUTE_AD_LOGOUT)

    def get_blueprint(self) -> list:      
        '''
        Creates a flask blueprint with specified url rules to allow static page routing
        '''       
        staticbp = Blueprint(self.name, self.__module__, template_folder='templates')
        rules = [
            ('/support', 'support', RouteController.render_support_page),
            ('/support/<path:path>', 'support_pages', RouteController.render_support_pages),
            ('/dataset/<dataset_id>/interest', 'dataset_interest', RouteController.update_dataset_interest),
            ('/tdh_partner_connect', 'tdh_partner_connect', RouteController.render_tdh_partner_connect_page),
            ('/tdh_partner_connect_file', 'tdh_partner_connect_file', RouteController.download_tdh_partner_connect_file)
        ]
        for rule in rules:
            staticbp.add_url_rule(*rule)

        return [staticbp, adauthbp, uploadbp, databricksbp]

    ''' 
    Modify dataset metadata fields
    '''  
    def _modify_package_schema(self, schema: Schema) -> Schema:
        # modify package schema with custom field
        schema.update({
            'availability': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')],
            'data_owners': [toolkit.get_validator('ignore_missing'),
                                toolkit.get_converter('convert_to_extras')],
            'data_quality': [toolkit.get_validator('ignore_missing'),
                                toolkit.get_converter('convert_to_extras')],
            'data_quality_score': [toolkit.get_validator('ignore_missing'),
                                toolkit.get_converter('convert_to_extras')],
            'data_stewards': [toolkit.get_validator('ignore_missing'),
                                toolkit.get_converter('convert_to_extras')],
            'expressed_interest': [toolkit.get_validator('ignore_missing'),
                                toolkit.get_converter('convert_to_extras')],
            'last_reviewed': [toolkit.get_validator('ignore_missing'),
                                toolkit.get_converter('convert_to_extras')]
        })
        schema['resources'].update({
                'resource_data_access': [toolkit.get_validator('ignore_missing')],
                'resource_data_category': [toolkit.get_validator('ignore_missing')]
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
            'availability': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')],
            'data_owners': [toolkit.get_converter('convert_from_extras'),
                              toolkit.get_validator('ignore_missing'),
                             toolkit.get_converter('convert_to_json_if_string')],
            'data_quality': [toolkit.get_converter('convert_from_extras'),
                                toolkit.get_validator('ignore_missing')],
            'data_quality_score': [toolkit.get_converter('convert_from_extras'),
                                toolkit.get_validator('ignore_missing')],
            'data_stewards': [toolkit.get_converter('convert_from_extras'),
                              toolkit.get_validator('ignore_missing'),
                             toolkit.get_converter('convert_to_json_if_string')],
            'expressed_interest': [toolkit.get_converter('convert_from_extras'),
                              toolkit.get_validator('ignore_missing')],
            'last_reviewed': [toolkit.get_converter('convert_from_extras'),
                                toolkit.get_validator('ignore_missing')]
        })
        schema['resources'].update({
                'resource_data_access': [toolkit.get_validator('ignore_missing')],
                'resource_data_category': [toolkit.get_validator('ignore_missing')]
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
    
    '''
    Override package search
    '''
    def before_dataset_search(self, search_params: dict) -> dict:
        if "fq" in search_params:
            patterns = {
                "res_format": r'res_format:"([^"]+)"',
                "res_data_access": r'res_data_access:"([^"]+)"',
                "res_data_category": r'res_data_category:"([^"]+)"'
            }

            for field, pattern in patterns.items():
                search_params["fq"] = re.sub(
                    pattern, 
                    lambda match: "{}:*{}*".format(field, match.group(1).replace(" ", "\\ ")), 
                    search_params["fq"]
                )

        return search_params

    def after_dataset_search(self, search_results, search_params):
        return search_results
    
    def before_dataset_index(self, pkg_dict):
        validated_data = pkg_dict.get('validated_data_dict')
        if not validated_data:
            return pkg_dict
        
        try:
            val_dict = json.loads(validated_data)
            res_dict = val_dict.get('resources', [])
            
            resource_data_access_types = list(set(
                    res.get('resource_data_access') for res in res_dict if res.get('resource_data_access')
            ))
            if resource_data_access_types:
                pkg_dict['res_data_access'] = ', '.join(resource_data_access_types)  

            resource_data_categories = list(set(
                    res.get('resource_data_category') for res in res_dict if res.get('resource_data_category')
            ))
            if resource_data_categories:
                pkg_dict['res_data_category'] = ', '.join(resource_data_categories)  

        except Exception as e:
            log.error(f"Failed to index custom dataset metadata: {e}")

        return pkg_dict
    
    def before_dataset_view(self, pkg_dict):
        return pkg_dict
    
    def read(self, entity):
        return entity

    def create(self, entity):
        return entity

    def edit(self, entity):
        return entity

    def delete(self, entity):
        return entity
    
    def after_dataset_create(self, context, pkg_dict):
        return pkg_dict

    def after_dataset_update(self, context, pkg_dict):
        return pkg_dict

    def after_dataset_delete(self, context, pkg_dict):
        return pkg_dict

    def after_dataset_show(self, context, pkg_dict):
        return pkg_dict

    '''
    Override search facets
    '''
    def dataset_facets(self, facets_dict, package_type):
        facets_dict['res_data_access'] = plugins.toolkit._('Data Access') 
        facets_dict['res_data_category'] = plugins.toolkit._('Data Category') 

        return facets_dict
    
    def organization_facets(self, facets_dict, organization_type, package_type):
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        return facets_dict
    
    '''
    Extend pages schema
    '''
    def update_pages_schema(self, schema):
        schema.update({
            'pin_page': [
                toolkit.get_validator('not_empty'),
                toolkit.get_validator('boolean_validator')]
            })
        return schema
