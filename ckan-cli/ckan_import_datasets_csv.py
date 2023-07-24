'''
Imports a list of datasets from a CSV file via the CKAN API.
Requires necessary publishers and topics to have been created.
'''

import argparse
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError
import csv
import json

parser = argparse.ArgumentParser("create_datasets", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--filename", dest="filename", help="Input file path", type=str, required=True)
parser.add_argument("--ckan_url", dest="ckan_url", help="Target CKAN instance.", default="http://localhost:5000", type=str)
parser.add_argument("--api_key", dest="api_key", help="API Key with necessary write permissions", type=str, required=True)
args = parser.parse_args()

count = 0

def upload_Dataset(dataset_dict):
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
            print(f"{err}. Data conflict in row {row}")
        else:
            print(err)

try:
    with open(args.filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        print("Running...")

        for row in reader:          
            # map the details of the dataset to create to a dict
            dataset_dict = {
                'name': row['Slug'], # required
                'title': row['Title'],
                'owner_org': row['Source'], # Publisher
                'private': False if row['Data Sharing Agreement Category'] else True,
                'notes': row['Description'] or "No description provided",
                'version': '1.0',
                'resources': [
                  {
                    'name': 'extract',
                    'path': row['Link to data'],
                    'format': row['File format'],
                    'description': row['Description']
                  }           
                ],
                'groups': [] if not row['Topics'] else list([{'name': topic.strip()} for topic in row['Topics'].split(';')]),
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
                  }         
                ]
            }
            upload_Dataset(dataset_dict)

except FileNotFoundError as err:
    print(err)

print(f'Added {count} total datasets.')
