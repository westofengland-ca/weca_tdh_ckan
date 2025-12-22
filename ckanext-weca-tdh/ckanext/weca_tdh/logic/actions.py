import json
import logging

import ckan.authz as authz
import ckan.plugins.toolkit as toolkit
import ckanext.weca_tdh.config as C

log = logging.getLogger(__name__)


def _user_can_view_page(user, visibility):
    """Return True if user is authorised to view a page with given visibility."""
    if visibility == 'restricted':
        return bool(user)
    elif visibility == 'private':
        return user and user.sysadmin
    return True


@toolkit.chained_action
@toolkit.side_effect_free
def pages_show(original_action, context, data_dict):
    page = original_action(context, data_dict)
    if not page:
        return None

    username = context.get('user')
    user = authz._get_user(username)
    visibility = page.get("visibility", "public")

    if not _user_can_view_page(user, visibility):
        toolkit.abort(401, toolkit._('Not authorised to see this page'))

    return page


@toolkit.chained_action
@toolkit.side_effect_free
def pages_list(original_action, context, data_dict):
    pages = original_action(context, data_dict)

    username = context.get('user')
    user = authz._get_user(username)
    
    return [
        page for page in pages
        if _user_can_view_page(user, page.get("visibility", "public"))
    ]


def _update_package_field_json(context, pkg_id: str, key: str, value: any) -> None:
    """Updates a package field json value.

    :param pkg_id: The dataset/package dict.
    :param key: Field key to update.
    :param value: New value for the key.
    """
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            value = [value]

    try:
        pkg_dict = toolkit.get_action('package_show')(context, {'id': pkg_id})
        pkg_dict[key] = json.dumps(value)

        toolkit.get_action('package_update')(context={'ignore_auth': True}, data_dict = pkg_dict)
    except Exception as e:
        log.warning(f"Failed to update package field {key} for pkg {pkg_id}: {e}", exc_info=True)


def _get_org_user_display_names(context, org_id):
    """Returns a list of member display names for an organisation."""
    try:
        members = toolkit.get_action('member_list')(context, {
            'id': org_id,
            'object_type': 'user'
        })
    except Exception as e:
        log.warning(f"Failed to fetch members for org {org_id}: {e}")
        return ['Unassigned']

    names_list = []

    for user_id, _, role in members:
        try:
            user = toolkit.get_action('user_show')(context, data_dict={'id': user_id})
            user_name = user.get(C.CKAN_USER_FULLNAME) or user.get('name')
            if user_name:
                names_list.append(user_name)
        except Exception as e:
            log.warning(f"Failed to fetch user with ID {user_id}: {e}")

    if not names_list:
        names_list.append('Unassigned')
    
    return names_list


def _get_org_package_ids(context, org_id):
    """Returns a list of package ids for a given owner org."""
    pkg_ids = []
    try:
        packages = toolkit.get_action('package_search')(context, {
            'q': f'owner_org:{org_id}', 
            'facet.limit': 1000, 
            'include_private': True})
        for pkg in packages['results']:
            pkg_ids.append(pkg['id'])

    except Exception as e:
        log.warning(f"Failed to get package list for org {org_id}: {e}")

    return pkg_ids


@toolkit.chained_action
def organization_member_create(original_action, context, data_dict):
    action = original_action(context, data_dict)
    user_names = _get_org_user_display_names(context, data_dict['id'])
    pkg_ids = _get_org_package_ids(context, data_dict['id'])

    for id in pkg_ids: 
        _update_package_field_json(context, id, 'data_owners', user_names)
    
    return action


@toolkit.chained_action
def organization_member_delete(original_action, context, data_dict):
    action = original_action(context, data_dict)
    user_names = _get_org_user_display_names(context, data_dict['id'])
    pkg_ids = _get_org_package_ids(context, data_dict['id'])
    
    for id in pkg_ids: 
        _update_package_field_json(context, id, 'data_owners', user_names)
    
    return action


def _get_collaborator_user_display_names(context, pkg_id):
    """Returns a list of collaborator display names for a package."""
    try:
        collaborators = toolkit.get_action('package_collaborator_list')(context, {'id': pkg_id})
    except Exception as e:
        log.warning(f"Failed to fetch collaborators for package {pkg_id}: {e}")
        return ['Unassigned']
    
    names_list = []
    ids_list = [user['user_id'] for user in collaborators]

    for ckan_id in ids_list:
        try:
            user = toolkit.get_action('user_show')(data_dict={C.CKAN_USER_ID: ckan_id})
            user_name = user.get(C.CKAN_USER_FULLNAME) or user.get('name')
            names_list.append(user_name)
        except Exception as e:
            log.warning(f"Failed to fetch user with ID {ckan_id}: {e}")

    if not names_list:
        names_list.append('Unassigned')
        
    return names_list


@toolkit.chained_action
def package_collaborator_create(original_action, context, data_dict):
    action = original_action(context, data_dict)
    user_names = _get_collaborator_user_display_names(context, data_dict['id'])
    _update_package_field_json(context, data_dict['id'], 'data_stewards', user_names)
    
    return action


@toolkit.chained_action
def package_collaborator_delete(original_action, context, data_dict):
    action = original_action(context, data_dict)
    user_names = _get_collaborator_user_display_names(context, data_dict['id'])
    _update_package_field_json(context, data_dict['id'], 'data_stewards', user_names)
    
    return action
