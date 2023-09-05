# CKAN user
CKAN_USER_ID = "id"
CKAN_USER_NAME = "name"
CKAN_USER_EMAIL = "email"
CKAN_USER_GIVEN_NAME = "given_name"
CKAN_USER_SURNAME = "surname"
CKAN_USER_FULLNAME = "fullname"

# CKAN roles
CKAN_ROLE_SYSADMIN = "sysadmin"

# CKAN routes
CKAN_ROUTE_AD_LOGIN = "/.auth/login/aad?post_login_redirect_url=/auth/aad"
CKAN_ROUTE_AD_LOGOUT = "/.auth/logout?post_logout_redirect_uri=/user/logged_out_redirect"

# AD Auth
AD_USER_ID = "X-Ms-Client-Principal-Id"
AD_USER_NAME = "X-Ms-Client-Principal-Name"
AD_ID_TOKEN = "X-Ms-Client-Principal"

# AD Claims
AD_CLAIM_URL = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims"
AD_CLAIM_TYPE = "typ"
AD_CLAIM_VALUE = "val"
AD_CLAIM_EMAIL = "emailaddress"
AD_CLAIM_GIVEN_NAME = "givenname"
AD_CLAIM_SURNAME = "surname"
AD_CLAIM_GROUPS = "groups"

# AD Groups
AD_GROUP_SYSADMIN_ID = "6e6f8da9-d632-468f-a698-db9436f4cd8a"

# Feature flags
FF_AUTH_EXTERNAL_ONLY = "feature_flag.auth.external_only"
FF_AD_UPDATE_USER = "feature_flag.ad.update_user"
FF_AD_SYSADMIN = "feature_flag.ad.sysadmin"
