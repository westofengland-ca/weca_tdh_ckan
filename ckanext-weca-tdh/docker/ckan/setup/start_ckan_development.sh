#!/bin/sh

# Set debug to true
echo "Enabling debug mode"
ckan config-tool $CKAN_INI -s DEFAULT "debug = true"

# Add ckan.datapusher.api_token to the CKAN config file (updated with corrected value later)
ckan config-tool $CKAN_INI ckan.datapusher.api_token=xxx

# Set secrets
ckan config-tool $CKAN_INI "SECRET_KEY=${CKAN_SECRET_KEY}"
ckan config-tool $CKAN_INI "WTF_CSRF_SECRET_KEY=${CKAN_SECRET_KEY}"
ckan config-tool $CKAN_INI "api_token.jwt.encode.secret=${CKAN_JWT_SECRET}"
ckan config-tool $CKAN_INI "api_token.jwt.decode.secret=${CKAN_JWT_SECRET}"

# Update the plugins setting in the ini file with the values defined in the env var
echo "Loading the following plugins: $CKAN__PLUGINS"
ckan config-tool $CKAN_INI "ckan.plugins = $CKAN__PLUGINS"

# Set the SQLAlchemy URL and CKAN core settings
ckan config-tool $CKAN_INI "sqlalchemy.url = $CKAN_SQLALCHEMY_URL" \
    "solr_url = $CKAN_SOLR_URL" \
    "ckan.redis.url = $CKAN_REDIS_URL" \
    "ckan.site_id = $CKAN_SITE_ID" \
    "ckan.site_url = $CKAN_SITE_URL" \
    "ckan.site_title = $CKAN_SITE_TITLE" \
    "ckan.site_description = $CKAN_SITE_DESCRIPTION"

# Set the session config
ckan config-tool $CKAN_INI SESSION_PERMANENT=False

# Set the search result configs
ckan config-tool $CKAN_INI ckan.group_and_organization_list_all_fields_max=1000
ckan config-tool $CKAN_INI search.facets.limit=1000
ckan config-tool $CKAN_INI search.facets.default=1000
ckan config-tool $CKAN_INI ckan.datasets_per_page=42

# Set the default user permissions
ckan config-tool $CKAN_INI ckan.auth.user_create_groups=False
ckan config-tool $CKAN_INI ckan.auth.user_create_organizations=False
ckan config-tool $CKAN_INI ckan.auth.create_dataset_if_not_in_organization=False
ckan config-tool $CKAN_INI ckan.auth.user_delete_organizations=False
ckan config-tool $CKAN_INI ckan.auth.user_delete_groups=False

# Set dataset level auth control
ckan config-tool $CKAN_INI "ckan.auth.allow_dataset_collaborators = $CKAN_AUTH_ALLOW_DATASET_COLLABORATORS"

# Set license group
ckan config-tool $CKAN_INI licenses_group_url=file:///$WECA_TDH_DIR/config/licenses.json

# Set resource formats
ckan config-tool $CKAN_INI ckan.resource_formats=$WECA_TDH_DIR/config/resource_formats.json

# Set the feature flag configs 
ckan config-tool $CKAN_INI "feature_flag.auth.restricted_access = $FEATURE_FLAG_AUTH_RESTRICTED_ACCESS"
ckan config-tool $CKAN_INI "feature_flag.auth.external_only = $FEATURE_FLAG_AUTH_EXTERNAL_ONLY"
ckan config-tool $CKAN_INI "feature_flag.auth.user_group_only = $FEATURE_FLAG_AUTH_USER_GROUP_ONLY"
ckan config-tool $CKAN_INI "feature_flag.ad.update_user = $FEATURE_FLAG_AD_UPDATE_USER"
ckan config-tool $CKAN_INI "feature_flag.ad.sysadmin = $FEATURE_FLAG_AD_SYSADMIN"
ckan config-tool $CKAN_INI "feature_flag.ga.enabled = $FEATURE_FLAG_GA_ENABLED"

# Set Azure AD user group id's
ckan config-tool $CKAN_INI "ad.group.ckan_id = $AD_USER_GROUP_CKAN_ID"
ckan config-tool $CKAN_INI "ad.group.sysadmin_id = $AD_USER_GROUP_SYSADMIN_ID"

# Set Cookie Control API key
ckan config-tool $CKAN_INI "ccc.api_key = $CCC_API_KEY" 

# Set Google Analytics config
ckan config-tool $CKAN_INI "ga.id = $GA_ID" 

# Set TDH contact email and phone number
ckan config-tool $CKAN_INI "tdh.contact_email = $TDH_CONTACT_EMAIL"
ckan config-tool $CKAN_INI "tdh.contact_phone_number = $TDH_CONTACT_PHONE_NUMBER"

# Set current build version
ckan config-tool $CKAN_INI "tdh.build_version = $TDH_BUILD_VERSION"

# Set partner connect file config
ckan config-tool $CKAN_INI "tdh.connect.address_host = $TDH_CONNECT_ADDRESS_HOST"
ckan config-tool $CKAN_INI "tdh.connect.address_path = $TDH_CONNECT_ADDRESS_PATH"

# Set Databricks app connection config
ckan config-tool $CKAN_INI "tdh.db_app.client_id = $TDH_DB_APP_CLIENT_ID"

# Set upload blob storage container connection
ckan config-tool $CKAN_INI "tdh.upload.storage_account = $TDH_UPLOAD_STORAGE_ACCOUNT"
ckan config-tool $CKAN_INI "tdh.upload.storage_container = $TDH_UPLOAD_STORAGE_CONTAINER"

# Set Logic App HTTP trigger url
decoded_url=$(echo "$TDH_UPLOAD_HTTP_TRIGGER" | sed 's/%2F/\//g')
ckan config-tool $CKAN_INI "tdh.upload.http_trigger = $decoded_url"

# Update test-core.ini DB, SOLR & Redis settings
echo "Loading test settings into test-core.ini"
ckan config-tool $SRC_DIR/ckan/test-core.ini \
    "sqlalchemy.url = $TEST_CKAN_SQLALCHEMY_URL" \
    "ckan.datastore.write_url = $TEST_CKAN_DATASTORE_WRITE_URL" \
    "ckan.datastore.read_url = $TEST_CKAN_DATASTORE_READ_URL" \
    "solr_url = $TEST_CKAN_SOLR_URL" \
    "ckan.redis.url = $TEST_CKAN_REDIS_URL"

# Configure logging
ckan config-tool $CKAN_INI --section logger_ckan "level = WARNING"
ckan config-tool $CKAN_INI --section logger_ckanext "level = WARNING"

# Configure token expiry
ckan config-tool $CKAN_INI expire_api_token.default_lifetime=30
ckan config-tool $CKAN_INI expire_api_token.default_unit=86400 # 1 day

# Configure pages
ckan config-tool $CKAN_INI "ckanext.pages.allow_html = True"

# Run the prerun script to init CKAN and create the default admin user
python3 prerun.py

echo "Set up ckan.datapusher.api_token in the CKAN config file"
ckan config-tool $CKAN_INI "ckan.datapusher.api_token=$(ckan -c $CKAN_INI user token add $CKAN_SYSADMIN_NAME datapusher expires_in=365 unit=86400 | tail -n 1 | tr -d '\t')"

CKAN_RUN="/usr/local/bin/ckan -c $CKAN_INI run -H 0.0.0.0"
CKAN_OPTIONS=""
if [ "$USE_DEBUGPY_FOR_DEV" = true ] ; then
    CKAN_RUN="/usr/local/bin/python -m debugpy --listen 0.0.0.0:5678 $CKAN_RUN"
    CKAN_OPTIONS="$CKAN_OPTIONS --disable-reloader"
fi

if [ "$USE_HTTPS_FOR_DEV" = true ] ; then
    CKAN_OPTIONS="$CKAN_OPTIONS -C unsafe.cert -K unsafe.key"
fi

# If the CKAN_JOB_MODE environment variable isn't set, run the HTTP server.
# Otherwise, rebuild the SOLR search index using the "only-missing" mode.
if [ -z "${CKAN_JOB_MODE}" ]
then
    while true; do
        $CKAN_RUN $CKAN_OPTIONS
        echo Exit with status $?. Restarting.
        sleep 2
    done
else
    echo "Running in job mode."
    if [ ${CKAN_INDEX_REBUILD_TYPE} == 'rebuild' ]
    then
        echo "Rebuilding entire search index."
        ckan search-index rebuild
    elif [ ${CKAN_INDEX_REBUILD_TYPE} == 'rebuild-clear' ]
    then
        echo "Rebuilding entire search index, clearing first."
        ckan search-index rebuild --clear
    elif [ ${CKAN_INDEX_REBUILD_TYPE} == 'clear' ]
    then
        echo "Clearing search index."
        ckan search-index clear
    else    
        echo "Rebuilding search index (missing packages only)"
        ckan search-index rebuild -o
    fi
fi
