FROM ckan/ckan-base:2.10.3

# Set up environment variables
ENV APP_DIR=/srv/app
ENV SRC_EXTENSIONS_DIR=/srv/app/src_extensions
ENV WECA_TDH_DIR=${SRC_EXTENSIONS_DIR}/ckanext-weca-tdh/ckanext/weca_tdh
ENV TZ=UTC
RUN echo ${TZ} > /etc/timezone

# Make sure both files are not exactly the same
RUN if ! [ /usr/share/zoneinfo/${TZ} -ef /etc/localtime ]; then \
        cp /usr/share/zoneinfo/${TZ} /etc/localtime ;\
    fi ;

# Override the default start_ckan script
COPY docker/ckan/setup/start_ckan.sh.override ${APP_DIR}/start_ckan.sh
RUN chmod +x ${APP_DIR}/start_ckan.sh

# Override the default prerun script
COPY docker/ckan/setup/prerun.py.override ${APP_DIR}/prerun.py

### Install TDH extension ###
COPY ./ ${APP_DIR}/src_extensions/ckanext-weca-tdh
RUN echo "pip install ckanext-weca-tdh..." && \
  pip3 install -r ${APP_DIR}/src_extensions/ckanext-weca-tdh/requirements.txt && \
  pip3 install -e ${APP_DIR}/src_extensions/ckanext-weca-tdh/
