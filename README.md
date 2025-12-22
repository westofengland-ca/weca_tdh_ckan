# weca_tdh_ckan

This repository contains content relating to the FTZ Transport Data Hub (TDH)
Data Catalogue. The TDH Data Catalogue has been developed as an extension of
CKAN, an open-source data management system.

## Contents

- .github
  - workflows
- ckan-cli
- ckanext-weca-tdh
  - docker

### .github/workflows

GitHub Actions workflow that is triggered on commit or PR to the
ckanext-weca-tdh directory. Currently runs CKAN unit tests.

### ckan-cli

Command Line Interface (CLI) tools for importing and exporting CKAN data using
the CKAN API.

### ckanext-weca-tdh

The CKAN extension for the WECA Transport Data Hub.

#### ckanext-weca-tdh/docker

Docker build to create a custom CKAN image containing the weca-tdh extension
for deployment and local development.

## Branching model

This repository uses Trunk Based Development see (https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development).
Work takes place on short-lived feature branches taken from and merging back
into the main branch. The main branch can then be deployed, as part of a CI/CD
process to a development environment.

Releases are generated from the main branch and are tagged using a semantic before being merged into the deploy/weca-prod branch.
