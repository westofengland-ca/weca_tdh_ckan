# ckanext-weca-tdh

CKAN extension containing templates and styling for WECA TDH Data Catalogue.

## Compatability

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.8 and earlier | not tested    |
| 2.9             | yes           |
| 2.10            | yes           |

## Docker Installation

Clone latest `ckan-docker`:

	git clone https://github.com/ckan/ckan-docker.git
	
Edit the `.env` file and add `weca_tdh` to the start of `CKAN__PLUGINS` list.

Clone latest `ckanext-weca-tdh` into `ckan-docker/src`:

	git clone https://github.com/RoweIT/ckanext-weca-tdh

`ckan-docker/src` is the mounted CKAN volume for local extensions.

Build the images:

	docker compose -f docker-compose.dev.yml build
	
Start the containers:

	docker compose -f docker-compose.dev.yml up

The image build will automatically install ‘requirements.txt’ and run ‘setup.py’ for the extension. 

## VM Installation

To install ckanext-weca-tdh on a vM:

Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

Clone the source and install it on the virtualenv


    cd /usr/lib/ckan/default/src
    
    git clone https://github.com/RoweIT/ckanext-weca-tdh.git
    
    
Install dependencies

    cd ckanext-weca-tdh  
    
    pip install -e . pip install -r requirements.txt
    
    npm install
	
Add `weca_tdh` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

Restart CKAN web server

     sudo supervisorctl restart ckan-uwsgi:*

### VM developer installation

To install ckanext-weca-tdh for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/RoweIT/ckanext-weca-tdh.git
    cd ckanext-weca-tdh
    python setup.py develop
    pip install -r dev-requirements.txt

## Local development
To develop the extension locally, clone the repository and cd to the `ckanext` directory. Then run `npm install` to install dependencies. To compile the styles you will need to have Sass installed and then run the script `npm run sass` to compile and watch for changes.

## Tests
TODO
To run the tests, do:

    pytest --ckan-ini=test.ini

## License
TODO
