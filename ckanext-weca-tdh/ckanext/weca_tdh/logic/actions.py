import ckan.authz as authz
import ckan.plugins.toolkit as toolkit


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
        toolkit.abort(401, toolkit._('Not authorized to see this page'))

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
