from ckan.common import config

# Global
CKAN_SITE_ID = config['ckan.site_id']
CKAN_SITE_URL= config['ckan.site_url']

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
CKAN_ROUTE_AD_LOGOUT = "/.auth/logout?post_logout_redirect_uri=/user/login"

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
AD_GROUP_SYSADMIN_ID = config.get('ad.group.sysadmin_id', "")

# Feature flags
FF_AUTH_RESTRICTED_ACCESS = config['feature_flag.auth.restricted_access']
FF_AUTH_EXTERNAL_ONLY = config['feature_flag.auth.external_only']
FF_AUTH_USER_GROUP_ONLY = config['feature_flag.auth.user_group_only']
FF_AD_UPDATE_USER = config.get('feature_flag.ad.update_user', "False")
FF_AD_SYSADMIN = config.get('feature_flag.ad.sysadmin', "False")
FF_GA_ENABLED = config.get('feature_flag.ga.enabled', "False")

# URL filter
EXLUDED_SUBPATHS = ('/about', '/accessibility', '/assets/', '/api/', '/base/', '/policy', '/scripts/', '/user/adlogin', '/user/login', '/webassets/')

# Flash messages
ALERT_MESSAGE_AUTH = "You must be logged in to access this page."
UPLOAD_STATUS_SUCCESS = "File uploaded successfully."
UPLOAD_STATUS_FAILED = "Failed to upload file."

contact_email = config.get('tdh.contact_email') or 'ftz@westofengland-ca.gov.uk'
ALERT_MESSAGE_SUPPORT_EMAIL = f"Contact support by emailing <a href='mailto:{contact_email}'>{contact_email}</a>"
ALERT_MESSAGE_SUPPORT = f"See the <a href='/about' target='_blank'><u>Support Page</u></a> for assistance raising a new issue on ServiceNow, quoting this error message"

# Cookie Control config
CCC_API_KEY = config['ccc.api_key']
CCC_LICENSE = 'PRO'

# Google Analytics config
GA_ID = config.get('ga.id', "")

# TDH partner connect file config
TDH_CONNECT_ADDRESS_HOST = config.get('tdh.connect.address_host', "")
TDH_CONNECT_ADDRESS_PATH = config.get('tdh.connect.address_path', "")

# TDH storage container config
TDH_UPLOAD_STORAGE_ACCOUNT = config.get('tdh.upload.storage_account', "")
TDH_UPLOAD_STORAGE_CONTAINER = config.get('tdh.upload.storage_container', "")
TDH_UPLOAD_FILE_TYPES = ['.csv', '.json', '.txt', '.xlsx', '.xml']
TDH_UPLOAD_FILE_SIZE = 16 * 1024 * 1024 # 16MB
TDH_UPLOAD_HTTP_TRIGGER = config.get('tdh.upload.http_trigger', "")

# Databricks Workspace config
TDH_DB_APP_CLIENT_ID = config.get('tdh.db_app.client_id', "")
TDH_DB_APP_REDIRECT_URL = f"{CKAN_SITE_URL}/databricks/auth"
