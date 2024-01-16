# ckanext-weca-tdh

CKAN extension for the TDH Data Catalogue. Adds custom functionality and themeing to CKAN.

Uses the [GOV.UK Design System](https://github.com/alphagov/govuk-design-system) in combination with [GOV.UK frontend Jinja macros](https://github.com/LandRegistry/govuk-frontend-jinja) for templates and styling, and Azure Active Directory (AD) for authentication.

## Compatability

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.8 and earlier | not tested    |
| 2.9             | yes           |
| 2.10            | yes           |

## Local development

### Docker installation
Clone latest `weca_tdh_ckan`:

	git clone https://github.com/westofengland-ca/weca_tdh_ckan.git

Go to docker directory:

	cd ckanext-weca-tdh/docker

Build the images:
##### dev build
	docker compose -f docker-compose.dev.yml build
 	docker compose -f docker-compose.dev.yml up

##### prod build
	docker compose build
 	docker compose up

The docker build will automatically install ‘requirements.txt’ and run ‘setup.py’ for the extension.

Live changes are enabled for templates. Any Python changes require a restart to the ckan container.

### VM installation

To install ckanext-weca-tdh on a CKAN VM:

Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

Clone the source and install it on the virtualenv
    
    git clone https://github.com/westofengland-ca/weca_tdh_ckan.git
    mv ckanext-weca-tdh /usr/lib/ckan/default/src   
    
Install dependencies

    cd ckanext-weca-tdh  
    
    pip install -e . pip install -r requirements.txt
    
    npm install
	
Add `weca_tdh` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

Restart CKAN web server

     sudo supervisorctl restart ckan-uwsgi:*

#### VM developer installation

To install ckanext-weca-tdh for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/RoweIT/ckanext-weca-tdh.git
    cd ckanext-weca-tdh
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests
Tests are run automatically on commit or PR via GitHub Actions.

To run the tests locally:

    pytest --ckan-ini=test.ini

## CKAN commands

### Promote user to sysadmin
To manually promote a user to a sysadmin, connect to the running CKAN instance using the Container App console and run commands:

 	ckan user list
  
  Returns a list of all users. Copy the username of the desired user.
  
	ckan sysadmin user add <username>
 
 Promotes user to a CKAN sysadmin.

 	ckan sysadmin list
  
  Returns a list of all sysadmins.

  	ckan sysadmin remove <username>
   
   Revokes a users sysadmin role.

  ### Rebuild Solr search index
  To manually rebuild the Solr search index, run command:

  	ckan search-index rebuild
