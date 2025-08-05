#!/bin/sh

# Add ckan.datapusher.api_token to the CKAN config file (updated with corrected value later)
ckan config-tool $CKAN_INI ckan.datapusher.api_token=xxx

# Set secrets
ckan config-tool $CKAN_INI "SECRET_KEY=${CKAN_SECRET_KEY}"
ckan config-tool $CKAN_INI "WTF_CSRF_SECRET_KEY=${CKAN_SECRET_KEY}"
ckan config-tool $CKAN_INI "api_token.jwt.encode.secret=${CKAN_JWT_SECRET}"
ckan config-tool $CKAN_INI "api_token.jwt.decode.secret=${CKAN_JWT_SECRET}"

# Set the SQLAlchemy (postgres) URL
ckan config-tool $CKAN_INI "sqlalchemy.url = $CKAN_SQLALCHEMY_URL"

# Set the SOLR URL
ckan config-tool $CKAN_INI "solr_url = $CKAN_SOLR_URL"

# Set the Redis URL
ckan config-tool $CKAN_INI "ckan.redis.url = $CKAN_REDIS_URL"

# Set the ckan site settings
ckan config-tool $CKAN_INI "ckan.site_id = $CKAN_SITE_ID"
ckan config-tool $CKAN_INI "ckan.site_url = $CKAN_SITE_URL"
ckan config-tool $CKAN_INI "ckan.site_title = $CKAN_SITE_TITLE"
ckan config-tool $CKAN_INI "ckan.site_description = $CKAN_SITE_DESCRIPTION"

# Set the Datapusher plugin config
ckan config-tool $CKAN_INI "ckan.datapusher.url = $CKAN_DATAPUSHER_URL"
ckan config-tool $CKAN_INI "ckan.datapusher.callback_url_base = $CKAN__DATAPUSHER__CALLBACK_URL_BASE"

# Set the Datastore plugin config
ckan config-tool $CKAN_INI "ckan.datastore.write_url = $CKAN_DATASTORE_WRITE_URL"
ckan config-tool $CKAN_INI "ckan.datastore.read_url = $CKAN_DATASTORE_READ_URL"

# Set the session config
ckan config-tool $CKAN_INI SESSION_PERMANENT=False
ckan config-tool $CKAN_INI SESSION_COOKIE_SECURE=True

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

# Set the common uwsgi options
UWSGI_OPTS="--socket /tmp/uwsgi.sock \
            --wsgi-file /srv/app/wsgi.py \
            --module wsgi:application \
            --http [::]:5000 \
            --master --enable-threads \
            --lazy-apps \
            -p 2 -L -b 32768 --vacuum \
            --harakiri $UWSGI_HARAKIRI"

if [ $? -eq 0 ]
then
    # If the CKAN_JOB_MODE environment variable isn't set, run the HTTP server.
    # Otherwise, rebuild the SOLR search index using the "only-missing" mode.
    if [ -z "${CKAN_JOB_MODE}" ]
    then
        # rebuild search index on container startup
        echo "Rebuilding solr search index."
        ckan search-index rebuild

        # Start uwsgi
        uwsgi $UWSGI_OPTS
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
            echo "Rebuilding search index (missing packages only)."
            ckan search-index rebuild -o
        fi
    fi
else
  echo "[prerun] failed...not starting CKAN."
fi
