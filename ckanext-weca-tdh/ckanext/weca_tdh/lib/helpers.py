import json
import logging
import time
from datetime import datetime
from typing import Any

import ckan.plugins.toolkit as toolkit
import ckanext.weca_tdh.config as C
from bs4 import BeautifulSoup
from ckanext.weca_tdh.redis_config import RedisConfig
from flask import flash
from markdown_it import MarkdownIt
from mdit_py_plugins.container import container_plugin
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

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

def sort_search_filter_items(filter_items: list, filter_type=None, checked_values=None) -> list:
    sorted_items = []
    seen_values = set()
    categories = get_resource_data_categories() if filter_type == 'res_data_category' else {}
    checked_set = set(checked_values or [])

    for item in filter_items:
        values = item['value'].split(', ') if ',' in item['value'] else [item['value']]
        for value in values:
            if value not in seen_values:
                seen_values.add(value)
                mapped_value = categories[int(value)].get('name', value) if value and categories else value
                checked = value in checked_set
                sorted_items.append({'value': value, 'text': mapped_value, 'checked': checked})

    return sorted_items

def get_orgs_or_groups_extras_list(is_org: bool, q: str = "") -> list:
    page_results: dict[str, Any] = {
        u'all_fields': True,
        u'q': q,
        u'include_extras': True,
        u'include_dataset_count': True,
        u'include_member_count': True,
    }

    action_name = 'organization_list' if is_org else 'group_list'
    data_dict = toolkit.get_action(action_name)(context={'ignore_auth': True}, data_dict=page_results)

    sorted_items = []
    seen_values = set()
    
    for item in data_dict:
        for extra in item.get('extras'):
            value = extra.get('value')
            if value and value not in seen_values:
                seen_values.add(value)
                sorted_items.append({'value': value, 'text': value})
    
    return sorted_items

def get_package_search_facets(facets: list[str], q: str = "") -> dict:
    data_dict: dict[str, Any] = {
        u'q': q,
        u'facet': True,
        u'facet.field': facets,
        u'facet.limit': -1, # unlimited
        u'rows': 0,
    }
    result = toolkit.get_action('package_search')(context={'ignore_auth': True}, data_dict=data_dict)
                
    return result.get('search_facets', {})

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
    
def user_has_valid_db_token() -> bool:
    """Checks if a valid Databricks access token exists in Redis for the current user.

    :return: True if access token exists and is not expired, otherwise False.
    """
    user = toolkit.current_user
    if not user:
        return False
    
    redis_client = RedisConfig(C.REDIS_URL)
    token_data = redis_client.get_databricks_tokens(user.id)
    if not token_data:
        return False

    access_token = token_data.get("access_token")
    expires_at = token_data.get("expires_at", 0)
    refresh_expires_at = token_data.get("refresh_expires_at", 0)

    now = time.time()

    try:
        return (
            bool(access_token)
            and (float(expires_at) > now or float(refresh_expires_at) > now)
        )
    except (TypeError, ValueError):
        return False


ALERT_ICONS = {
    "note": "<i class='fa-solid fa-circle-info markdown-alert-icon'></i>",
    "tip": "<i class='fa-solid fa-lightbulb markdown-alert-icon'></i>",
    "important": "<i class='fa-solid fa-flag markdown-alert-icon'></i>",
    "warning": "<i class='fa-solid fa-triangle-exclamation markdown-alert-icon'></i>",
    "caution": "<i class='fa-solid fa-circle-exclamation markdown-alert-icon'></i>"
}

def _render_container_alert(name: str):
    icon = ALERT_ICONS.get(name, "")
    def _render(self, tokens, idx, _options, _env):
        if tokens[idx].nesting == 1:
            return f'<div class="markdown-alert markdown-alert-{name}"> \
                <p class="markdown-alert-title">{icon} <strong>{name.title()}</strong></p>\n'
        else:
            return '</div>\n'
    return _render

def render_markdown_gfm(content: str) -> str:
    md = MarkdownIt("gfm-like") \
        .use(footnote_plugin) \
        .use(front_matter_plugin) \
        .use(deflist_plugin) \
        .use(tasklists_plugin)
        
    container_types = ["note", "tip", "important", "warning", "caution"]
    for name in container_types:
        md.use(container_plugin, name=name, render=_render_container_alert(name))

    html = md.render(content)
    soup = BeautifulSoup(html, "html.parser")

    for table in soup.find_all("table"):
        table["class"] = table.get("class", []) + ["govuk-table"]

        thead = table.find("thead")
        if thead:
            thead["class"] = thead.get("class", []) + ["govuk-table__head"]
            
        tbody = table.find("tbody")
        if tbody:
            thead["class"] = thead.get("class", []) + ["govuk-table__body govuk-body-s"]

        for tr in table.find_all("tr"):
            tr["class"] = tr.get("class", []) + ["govuk-table__row"]

            for th in tr.find_all("th"):
                th["class"] = th.get("class", []) + ["govuk-table__header"]
            for td in tr.find_all("td"):
                td["class"] = td.get("class", []) + ["govuk-table__cell"]
        
    return str(soup)
