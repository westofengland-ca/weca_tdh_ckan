FROM ckan/ckan-base:2.11.1

# Set up environment variables
ENV APP_DIR=/srv/app

# Override the default start_ckan script
COPY --chown=ckan-sys:ckan-sys docker/ckan/setup/start_ckan.sh ${APP_DIR}

# Override the default prerun script
COPY --chown=ckan-sys:ckan-sys docker/ckan/setup/prerun.py ${APP_DIR}

# Mount TDH extension
COPY --chown=ckan:ckan-sys ./ ${APP_DIR}/src_extensions/ckanext-weca-tdh

# Install TDH extension
RUN echo "pip install ckanext-weca-tdh..." && \
  pip3 install -r ${APP_DIR}/src_extensions/ckanext-weca-tdh/requirements.txt && \
  pip3 install -e ${APP_DIR}/src_extensions/ckanext-weca-tdh/

# Install any patches
COPY --chown=ckan-sys:ckan-sys docker/ckan/patches ${APP_DIR}/patches
RUN for d in $APP_DIR/patches/*; do \
        if [ -d $d ]; then \
            for f in `ls $d/*.patch | sort -g`; do \
                cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
            done ; \
        fi ; \
    done
