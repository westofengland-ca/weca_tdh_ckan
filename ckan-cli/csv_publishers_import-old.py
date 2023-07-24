import argparse
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError
import csv
import json
import re

parser = argparse.ArgumentParser("create_orgs", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--filename", dest="filename", help="Input file path", type=str, required=True)
parser.add_argument("--ckan_url", dest="ckan_url", help="Target CKAN instance.", default="http://localhost:5000", type=str)
parser.add_argument("--api_key", dest="api_key", help="API Key with necessary write permissions", type=str, required=True)
args = parser.parse_args()

count = 0

def uploadOrg(org_dict):
    # Use the json module to dump the dictionary to a string for posting. URL encode.
    data_string = quote(json.dumps(org_dict)).encode('utf-8')

    # CKAN package_create function creates a new dataset.
    request = Request(f'{args.ckan_url}/api/action/organization_create')

    # Creating a dataset requires an authorization header.
    # provide API key from your user account on the CKAN site that you're creating the dataset on.
    request.add_header('Authorization', args.api_key)

    # Make the HTTP request.
    try:
        response = urlopen(request, data_string)
        assert response.code == 200

        global count 
        count += 1
    except HTTPError as err:
        if err.code == 409:
            print(f"{err}. Data conflict in row {row['ID']}")
        else:
            print(err)

def formatOrgName(string):
    # removes any character that are not alphanumeric or underscores.
    sanitised_string = re.sub(r'[^a-zA-Z0-9\s_]', '', string)
    
    # replace spaces with underscores
    sanitised_string = re.sub(r'\s+', '_', sanitised_string)
    return sanitised_string.lower()

def formatOrgID(string):
    # removes any character that are not alphanumeric.
    sanitised_string = re.sub(r'[^a-zA-Z0-9]', '', string)
    return sanitised_string.lower()

try:
    with open(args.filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        print("Running...")

        for row in reader:
            if not row['Source']:
                continue
            
            org_dict = {
                'name': formatOrgName(row['Source']),
                'id': formatOrgID(row['Source']),
                'title': row['Source']
            }

            uploadOrg(org_dict)

except FileNotFoundError as err:
    print(err)

print(f'Created {count} total Publishers.')
