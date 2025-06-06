import json
import logging
from datetime import datetime

import ckan.plugins.toolkit as toolkit
import ckanext.weca_tdh.config as C
from ckanext.weca_tdh.databricks import oauth_code_verify_and_challenge
from flask import flash, session

log = logging.getLogger(__name__)


def filter_datetime(string: str, format: str = 'full') -> str:
    try:
        dt = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%f')   

    except (ValueError, TypeError):
        try:
            dt = datetime.strptime(string, '%Y-%m-%d')
        except Exception:
            return ""

    if format == 'short':
        return dt.strftime('%d %b %Y')      
 
    return dt.strftime('%d %b %Y %H:%M:%S')

def get_cookie_control_config() -> dict:
    cookie_control_config = {}

    api_key = C.CCC_API_KEY
    cookie_control_config['api_key'] = api_key

    license_type = C.CCC_LICENSE
    cookie_control_config['license_type'] = license_type

    return cookie_control_config

def get_google_analytics_config() -> dict:
    google_analytics_config = {}

    ga_id = C.GA_ID
    google_analytics_config['ga_id'] = ga_id

    return google_analytics_config

def get_resource_data_categories() -> list:
    data_categories = [{
        "id": 0,
        "name": "Open",
        "desc": "Can be accessed by anyone (with access to the TDH).",
        "class": "data-category-open"
      },
      {
        "id": 1,
        "name": "Controlled",
        "desc": "Can be accessed by defined teams or persons.",
        "class": "data-category-cont"
      },
      {
        "id": 2,
        "name": "Controlled (Personal Info)",
        "desc": "Subject to GDPR; only accessible by relevant teams or persons.",
        "class": "data-category-contpi"
      },
      {
        "id": 3,
        "name": "Confidential",
        "class": "data-category-con"
    }]

    return data_categories

def get_data_quality_markings() -> list:
    data_quality_markings = [{
        "id": 0,
        "name": "Unclassified",
        "score": "Unclassified",
      },
      {
        "id": 1,
        "name": "Poor",
        "score": "<45",
      },
      {
        "id": 2,
        "name": "Moderate",
        "score": "45-54",
      },
      {
        "id": 3,
        "name": "Good",
        "score": "55-64",
      },
      {
        "id": 4,
        "name": "Excellent",
        "score": "65-76",
    }]

    return data_quality_markings

def get_featured_datasets(limit_new: int, limit_upcoming: int) -> dict:
    data_dict = {
        'fq': '-availability:upcoming',
        'sort': 'metadata_created desc',
        'rows': limit_new
    }
    package_list_new = toolkit.get_action('package_search')(context = {'ignore_auth': True}, data_dict = data_dict)
    package_list_new = package_list_new.get('results')
    
    data_dict = {
        'fq': 'availability:upcoming',
        'rows': limit_upcoming
    }
    package_list_upcoming = toolkit.get_action('package_search')(context = {'ignore_auth': True}, data_dict = data_dict)
    package_list_upcoming = package_list_upcoming.get('results')

    return package_list_new + package_list_upcoming

def get_featured_blog_articles(limit: int, exclude=None) -> dict:
    blog_list = toolkit.get_action('ckanext_pages_list')(None, {'order_publish_date': True, 'private': False, 'page_type': 'blog'})
    featured_list = []

    for blog in blog_list:
        if exclude and blog['name'] == exclude:
            continue
        featured_list.append(blog)
        if len(featured_list) == limit:
            break

    return featured_list

def sort_search_filter_items(filter_items: list, filter_type=None, selected_values=None) -> list:
    sorted_items = []
    seen_values = set()
    categories = get_resource_data_categories() if filter_type == 'res_data_category' else {}
    selected_set = set(selected_values or [])

    for item in filter_items:
        values = item['value'].split(', ') if ',' in item['value'] else [item['value']]
        for value in values:
            if value not in seen_values:
                seen_values.add(value)
                mapped_value = categories[int(value)].get('name', value) if value and categories else value
                selected = value in selected_set
                sorted_items.append({'value': value, 'text': mapped_value, 'selected': selected})

    return sorted_items

def sort_custom_metadata(page_items: list, current_filter: str) -> list:  
    sorted_items = [{'value': "", 'text': ""}]

    # Set to track seen values
    seen_values = set()
    
    for item in page_items:
        for extra in item.get('extras'):
            value = extra.get('value')
            if extra.get('key') == 'parent_org' and value and value not in seen_values:
                # Add the value to the seen set
                seen_values.add(value)
                 
                # Create new entries for each unique value
                sorted_items.append({
                    'value': value, 
                    'text': value,
                    'selected': value == current_filter
                })
    
    return sorted_items

def update_package_metadata(pkg_dict: dict, key: str, value: any) -> dict:
    pkg_dict[key] = value
    return toolkit.get_action('package_update')(context = {'ignore_auth': True}, data_dict = pkg_dict)

def update_package_metadata_list(pkg_dict: dict, key: str, value: any) -> dict:
    existing = pkg_dict.get(key, '')
    existing_values = [v.strip() for v in existing.split(',')] if existing else []

    if value in existing_values:
        flash("You've already expressed interest in this dataset.", category='alert-info')
    else:
        existing_values.append(value)
        pkg_dict[key] = ', '.join(existing_values)
        flash("Thanks! Your interest has been recorded.", category='alert-success')

    return toolkit.get_action('package_update')(context = {'ignore_auth': True}, data_dict = pkg_dict)

def transform_collaborators(collaborators: tuple) -> str:
    ids_list = [user[0] for user in collaborators]
    names_list = []

    for ckan_id in ids_list:
        try:
            user = toolkit.get_action('user_show')(data_dict={C.CKAN_USER_ID: ckan_id})
            names_list.append(user[C.CKAN_USER_FULLNAME])
        except Exception as e:
            log.error(f"Failed to fetch user with ID {ckan_id}: {e}")

    if names_list:
        return json.dumps(names_list)
    else:
        names_list.append('Unassigned')
        return json.dumps(names_list)
    
def transform_data_owners(data_owners: dict) -> str:
    names_list = [user[C.CKAN_USER_FULLNAME] for user in data_owners]

    if names_list:
        return json.dumps(names_list)
    else:
        names_list.append('Unassigned')
        return json.dumps(names_list)
    
def json_loads(string_list):
    if not string_list:
        return []

    try:
        parsed_list = json.loads(string_list)
        clean_list = [str(item) for item in parsed_list if item is not None]

        return clean_list
    except (json.JSONDecodeError, TypeError):
        return []

def build_databricks_auth_url(resource_id: str, referrer: str) -> str:
    client_id = C.TDH_DB_APP_CLIENT_ID
    redirect_url = C.TDH_DB_APP_REDIRECT_URL
    
    code_verifier, code_challenge = oauth_code_verify_and_challenge()
    session['code_verifier'] = code_verifier
    session['referrer'] = referrer
    
    url = f"https://{C.TDH_CONNECT_ADDRESS_HOST}/oidc/v1/authorize" + \
        f"?client_id={client_id}" + \
        f"&redirect_uri={redirect_url}" + \
        "&response_type=code" + \
        f"&state={resource_id}" + \
        f"&code_challenge={code_challenge}" + \
        "&code_challenge_method=S256" + \
        "&scope=all-apis+offline_access"
        
    return url