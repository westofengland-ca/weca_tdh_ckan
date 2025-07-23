import json
import logging
import re
import time
from datetime import datetime
from typing import Any

import ckan.plugins.toolkit as toolkit
import ckanext.weca_tdh.config as C
from bs4 import BeautifulSoup
from ckanext.weca_tdh.redis_config import RedisConfig
from flask import flash
from markdown import markdown
from markdown_it import MarkdownIt
from mdit_py_plugins.container import container_plugin
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

log = logging.getLogger(__name__)


def filter_datetime(string: str, format: str = 'full') -> str:
    """Parses a datetime string and returns it in a human-readable format.

    :param string: The datetime string to format.
    :param format: The format to use, either 'full' or 'short'.
    :return: Formatted datetime string or empty string if parsing fails.
    """
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


def strip_markdown(text: str) -> str:
    """Strips markdown from a text field
    
    :param string: The input text containing markdown
    :return: Raw text
    """
    html = markdown(text or '')
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


def extract_markdown_description(text: str) -> str:
    """Extracts description section from markdown text
    
    param string: The input text containing markdown
    return: The text content following a Description heading
    """
    if not text:
        return ''

    pattern = re.compile(
        r'(?i)^#{1,6}\s*description\s*\n?(.*?)(?=^#{1,6}\s*\S|\Z)', 
        re.MULTILINE | re.DOTALL
    )

    match = pattern.search(text)
    if not match:
        return ''

    section = match.group(1).strip()
    html = markdown(section)
    soup = BeautifulSoup(html, 'html.parser')

    return soup.get_text(separator=' ').strip()


def get_cookie_control_config() -> dict:
    """Returns the configuration dict for Cookie Control.

    :return: Dict containing API key and license type.
    """
    return {
        'api_key': C.CCC_API_KEY,
        'license_type': C.CCC_LICENSE,
    }


def get_google_analytics_config() -> dict:
    """Returns the configuration dict for Google Analytics.

    :return: Dictcontaining the GA tracking ID.
    """
    return {
        'ga_id': C.GA_ID,
    }


def get_resource_data_categories() -> list:
    """Returns a predefined list of data access categories.

    :return: List of dicts describing access levels and labels.
    """
    return [
        {"id": 0, "name": "Open", "desc": "Can be accessed by anyone (with access to the TDH).", "class": "data-category-open"},
        {"id": 1, "name": "Controlled", "desc": "Can be accessed by defined teams or persons.", "class": "data-category-cont"},
        {"id": 2, "name": "Controlled (Personal Info)", "desc": "Subject to GDPR; only accessible by relevant teams or persons.", "class": "data-category-contpi"},
        {"id": 3, "name": "Confidential", "class": "data-category-con"}
    ]


def get_data_quality_markings() -> list:
    """Returns a predefined list of data quality stats.

    :return: List of dicts describing data quality markings and scores.
    """
    return [
        {"id": 0, "name": "Unclassified", "score": "Unclassified"},
        {"id": 1, "name": "Poor", "score": "<45"},
        {"id": 2, "name": "Moderate", "score": "45-54"},
        {"id": 3, "name": "Good", "score": "55-64"},
        {"id": 4, "name": "Excellent", "score": "65-76"},
    ]


def get_featured_datasets(limit_new: int, limit_upcoming: int) -> dict:
    """Gets a combined list of newly added and upcoming datasets.

    :param limit_new: Number of new datasets to retrieve.
    :param limit_upcoming: Number of upcoming datasets to retrieve.
    :return: Combined list of datasets.
    """
    data_dict = {
        'fq': 'availability:available',
        'sort': 'metadata_created desc',
        'rows': limit_new
    }
    package_list_new = toolkit.get_action('package_search')(context = {'ignore_auth': True}, data_dict = data_dict)
    package_list_new = package_list_new.get('results')
    
    data_dict = {
        'fq': 'availability:upcoming',
        'sort': 'metadata_created desc',
        'rows': limit_upcoming
    }
    package_list_upcoming = toolkit.get_action('package_search')(context = {'ignore_auth': True}, data_dict = data_dict)
    package_list_upcoming = package_list_upcoming.get('results')

    return package_list_new + package_list_upcoming


def get_featured_blog_articles(limit: int, exclude=None) -> dict:
    """Gets a list of featured blog articles.

    :param limit: Maximum number of articles to return.
    :param exclude: Optional name of an article to exclude.
    :return: List of featured articles.
    """
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
    """Sorts and formats extra filter items for display in the UI.

    :param filter_items: List of filter items.
    :param filter_type: Optional filter type for mapping values.
    :param checked_values: List of selected filter values.
    :return: Sorted and formatted filter items.
    """
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
    """Gets a list of unique extra values from organisations or groups.

    :param is_org: True to query organisations, False for groups.
    :param q: Optional search query.
    :return: List of unique extras.
    """
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


def get_package_search_facets(facets: list[str], q: str = "", include_private=False) -> dict:
    """Gets facet information for the given fields using the package search API.

    :param facets: List of fields to facet on.
    :param q: Optional search query.
    :return: Dict of facet counts per field.
    """
    data_dict: dict[str, Any] = {
        u'q': q,
        u'facet': True,
        u'facet.field': facets,
        u'facet.limit': -1, # unlimited
        u'rows': 0,
        u'include_private': include_private
    }
    result = toolkit.get_action('package_search')(context={'ignore_auth': True}, data_dict=data_dict)
                
    return result.get('search_facets', {})


def update_package_metadata(pkg_dict: dict, key: str, value: any) -> dict:
    """Updates a metadata key on a package.

    :param pkg_dict: The dataset/package dict.
    :param key: Metadata key to update.
    :param value: New value for the key.
    :return: Updated package dict.
    """
    pkg_dict[key] = value
    return toolkit.get_action('package_update')(context = {'ignore_auth': True}, data_dict = pkg_dict)


def update_package_metadata_list(pkg_dict: dict, key: str, value: any) -> dict:
    """Appends a value to a comma-separated list in a package metadata field.

    :param pkg_dict: The dataset/package dict.
    :param key: Metadata key to append to.
    :param value: Value to add.
    :return: Updated package dict.
    """
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
    """Converts a tuple of collaborator user IDs into a JSON list of full names.

    :param collaborators: Tuple of (user_id, ...) values.
    :return: JSON string of user full names.
    """
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
    """Converts a list of data owner user objects into a JSON list of full names.

    :param data_owners: List of user dicts.
    :return: JSON string of user full names.
    """
    names_list = [user[C.CKAN_USER_FULLNAME] for user in data_owners]

    if names_list:
        return json.dumps(names_list)
    else:
        names_list.append('Unassigned')
        return json.dumps(names_list)
    

def json_loads(string_list):
    """Safely loads a JSON list from a string.

    :param string_list: JSON-encoded string.
    :return: List of stringified elements or empty list if parsing fails.
    """
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
    "note": "fa-solid fa-circle-info",
    "tip": "fa-solid fa-lightbulb",
    "important": "fa-solid fa-flag",
    "warning": "fa-solid fa-triangle-exclamation",
    "caution": "fa-solid fa-circle-exclamation"
}

def _render_container_alert(name: str):
    icon = ALERT_ICONS.get(name, "")
    def _render(self, tokens, idx, _options, _env):
        if tokens[idx].nesting == 1:
            return f'<div class="markdown-alert markdown-alert-{name}"> \
                <p class="markdown-alert-title"><i class="{icon} markdown-alert-icon"></i> \
                    <strong>{name.title()}</strong></p>\n'
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
