# weca_tdh_ckan

This repository contains content relating to the FTZ Transport Data Hub (TDH)
data catalogue. The TDH data catalogue has been developed as an extension of
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

This repository uses a standard Gitflow Workflow (see
https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
with work being developed on feature branches taken from a develop branch. The
develop branch can then be deployed, as part of a CI/CD process to a development
environment. main and release branches are used to control the release of
code with release builds being built from the release branches.

The development environment will deploy from the develop branch. The preprod
and prod environments have no build process. CKAN is deployed to these environments
from containers built from release branches. Semantic version numbering will be
used to mange the releases.

This primarily affects the CKAN docker container - but by keeping everything in
the same repository and managing it as a whole then all the CKAN artefacts (CLI,
extension, docker container) are all kept aligned form a coherent package that
works together.