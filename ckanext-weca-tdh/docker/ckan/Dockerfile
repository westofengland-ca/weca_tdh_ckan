FROM ckan/ckan-base:2.11.1-py3.10

# Set up environment variables
ENV APP_DIR=/srv/app
ENV SRC_EXTENSIONS_DIR=/srv/app/src_extensions
ENV WECA_TDH_DIR=${SRC_EXTENSIONS_DIR}/ckanext-weca-tdh/ckanext/weca_tdh

# Override the default start_ckan script
COPY --chown=ckan-sys:ckan-sys docker/ckan/setup/start_ckan.sh ${APP_DIR}

# Override the default prerun script
COPY --chown=ckan-sys:ckan-sys docker/ckan/setup/prerun.py ${APP_DIR}

# Mount TDH extension
COPY --chown=ckan:ckan-sys ./ ${SRC_EXTENSIONS_DIR}/ckanext-weca-tdh

USER root
RUN mkdir /srv/app/.local && chown ckan /srv/app/.local
# Create the storage directory if it doesn't exist and set ownership
RUN mkdir -p /var/lib/ckan/storage && chown -R ckan:ckan-sys /var/lib/ckan/storage
RUN chmod +x ${APP_DIR}/start_ckan.sh
USER ckan

# Install TDH extension
RUN echo "pip install ckanext-weca-tdh..." && \
  pip3 install -r ${SRC_EXTENSIONS_DIR}/ckanext-weca-tdh/requirements.txt && \
  pip3 install -e ${SRC_EXTENSIONS_DIR}/ckanext-weca-tdh/
