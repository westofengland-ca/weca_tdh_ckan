import argparse
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError
import csv
import json
import re

parser = argparse.ArgumentParser("create_datasets", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--filename", dest="filename", help="Input file path", type=str, required=True)
parser.add_argument("--ckan_url", dest="ckan_url", help="Target CKAN instance.", default="http://localhost:5000", type=str)
parser.add_argument("--api_key", dest="api_key", help="API Key with necessary write permissions", type=str, required=True)
args = parser.parse_args()

count = 0

def uploadDataset(dataset_dict):
    # Use the json module to dump the dictionary to a string for posting. URL encode.
    data_string = quote(json.dumps(dataset_dict)).encode('utf-8')

    # CKAN package_create function creates a new dataset.
    request = Request(f'{args.ckan_url}/api/action/package_create')

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

def formatDatasetName(string):
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
            if not row['Title'] or not row['Source']:
                print(f"ID: {row['ID']}. Invalid or missing title/source - Skipped.")
                continue
            
            # map the details of the dataset to create into a dict
            dataset_dict = {
                'name': formatDatasetName(row['Title']), # required
                'title': row['Title'],
                'owner_org': formatOrgID(row['Source']), # Publisher
                'private': False if row['Data Sharing Agreement Category'] else True,
                'notes': row['Description'] or "No description provided",
                'url': row['Source'], # source of dataset (Publisher)
                'version': '1.0',
                'resources': [
                  {
                    'name': 'extract',
                    'path': row['Link to data'],
                    'format': row['File format'],
                    'description': row['Description']
                  }           
                ],
                'extras': [ # custom fields
                  {
                    'key': 'Data type',
                    'value': row['Data type']
                  },
                  {
                    'key': 'Method of transfer',
                    'value': row['Method of transfer']
                  },
                  {
                    'key': 'Volume',
                    'value': row['Volume']
                  },
                  {
                    'key': 'Frequency of change',
                    'value': row['Frequency of change']
                  },
                  {
                    'key': 'Data Owner',
                    'value': row['Data Owner']
                  },
                  {
                    'key': 'Data agreements',
                    'value': row['Data agreements']
                  },
                  {
                    'key': 'Status',
                    'value': row['Status']
                  },
                  {
                    'key': 'Contact',
                    'value': row['Contact']
                  },
                  {
                    'key': 'Data Sharing Agreement Category',
                    'value': row['Data Sharing Agreement Category']
                  },
                  {
                    'key': 'Last retention review date',
                    'value': row['Last retention review date']
                  }, 
                  {
                    'key': 'Retention review period',
                    'value': row['Retention review period']
                  }           
                ]
            }

            uploadDataset(dataset_dict)

except FileNotFoundError as err:
    print(err)

print(f'Added {count} total datasets.')
