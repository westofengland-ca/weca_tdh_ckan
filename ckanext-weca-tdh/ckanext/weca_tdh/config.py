from ckan.common import config

# CKAN user
CKAN_USER_ID = "id"
CKAN_USER_NAME = "name"
CKAN_USER_EMAIL = "email"
CKAN_USER_FULLNAME = "fullname"
CKAN_USER_STATE = 'state'

# CKAN roles
CKAN_ROLE_SYSADMIN = "sysadmin"

# CKAN routes
CKAN_ROUTE_AD_LOGIN = "/.auth/login/aad?post_login_redirect_url=/auth/aad"
CKAN_ROUTE_AD_LOGOUT = "/.auth/logout?post_logout_redirect_uri=/user/logged_out_redirect"

# AD Auth
AD_USER_ID = "X-Ms-Client-Principal-Id"
AD_ID_TOKEN = "X-Ms-Client-Principal"
AD_SESSION_COOKIE = 'AppServiceAuthSession'

# AD Claims
AD_CLAIM_URL = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims"
AD_CLAIM_TYPE = "typ"
AD_CLAIM_VALUE = "val"
AD_CLAIM_EMAIL = "emailaddress"
AD_CLAIM_NAME = 'name'
AD_CLAIM_GROUPS = "groups"

# AD Groups
AD_GROUP_CKAN_ID = config['ad.group.ckan_id']
AD_GROUP_SYSADMIN_ID = config['ad.group.sysadmin_id']

# Feature flags
FF_AUTH_EXTERNAL_ONLY = config['feature_flag.auth.external_only']
FF_AUTH_USER_GROUP_ONLY = config['feature_flag.auth.user_group_only']
FF_AD_UPDATE_USER = config['feature_flag.ad.update_user']
FF_AD_SYSADMIN = config['feature_flag.ad.sysadmin']

# URL filter
EXLUDED_SUBPATHS = ('/assets/', '/api/', '/base/', '/scripts/', '/webassets/')

# Cookie config
CC_API_KEY = config['cc.api_key']
CC_LICENSE = 'community' # update to new subscription
CC_INITIAL_STATE = 'notify'
