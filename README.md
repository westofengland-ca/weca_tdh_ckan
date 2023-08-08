# weca_tdh_ckan
This repository contains content relating to the FTZ Transport Data Hub (TDH) data catalogue. The TDH data catalogue has been developed as an extension of CKAN, an open-source data management system.

## Contents
- workflows
- ckan-cli
- ckanext-weca-tdh
  - docker

### workflows
GitHub Actions workflow that is triggered on commit or PR to the ckanext-weca-tdh directory. Currently runs CKAN unit tests.

### ckan-cli
Command Line Interface (CLI) tools for importing and exporting CKAN data using the CKAN API.

### ckanext-weca-tdh
The CKAN extension for the WECA Transport Data Hub.

#### docker
Docker build to create a custom CKAN image containing the weca-tdh extension for deployment and local development.
