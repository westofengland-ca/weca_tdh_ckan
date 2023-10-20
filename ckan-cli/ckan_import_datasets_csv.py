'''
Imports a list of datasets from a CSV file via the CKAN API.
Requires necessary publishers and topics to have been created.
'''

import argparse
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import URLError, HTTPError
import csv
import json
import csv_column_headers

parser = argparse.ArgumentParser("create_datasets", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--filename", dest="filename", help="Input file path", type=str, required=True)
parser.add_argument("--ckan_url", dest="ckan_url", help="Target CKAN instance.", default="http://localhost:5000", type=str)
parser.add_argument("--api_key", dest="api_key", help="API Key with necessary write permissions", type=str, required=True)
args = parser.parse_args()

def import_dataset(dataset_dict):
    # Use the json module to dump the dictionary to a string for posting. URL encode.
    data_string = quote(json.dumps(dataset_dict)).encode('utf-8')

    # CKAN package_create function creates a new dataset.
    request = Request(f'{args.ckan_url}/api/action/package_create')

    # Creating a dataset requires an authorization header.
    # provide API key from your user account on the CKAN site that you're creating the dataset on.
    request.add_header('Authorization', args.api_key)

    # Make the HTTP request.
    try:
        urlopen(request, data_string)
    except HTTPError as err:
        if err.code == 409:
            raise Exception(f'import_dataset(): data conflict in row {row}')
        raise Exception(f'import_dataset(): failed to import dataset. {err}')
    except URLError:
        raise Exception(f'import_dataset(): invalid URL')

try:
    with open(args.filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        print("Running...")
        
        for row in reader:          
            # map the details of the dataset to create to a dict
            dataset_dict = {
                'name': row[csv_column_headers.DATASET_SLUG], # required
                'title': row[csv_column_headers.DATASET_TITLE],
                'owner_org': row[csv_column_headers.DATASET_PUBLISHER], # Publisher
                'private': False if row[csv_column_headers.DATASET_VISIBILITY] else True,
                'notes': row[csv_column_headers.DATASET_DESC] or "No description provided",
                'resources': [
                  {
                    'name': row[csv_column_headers.DATASET_TITLE],
                    'url': row[csv_column_headers.DATASET_RESOURCE_PATH],
                    'format': row[csv_column_headers.DATASET_RESOURCE_FORMAT],
                    'description': row[csv_column_headers.DATASET_RESOURCE_DESC] or "No description provided"
                  }           
                ],
                'groups': [] if not row[csv_column_headers.DATASET_TOPICS] else list([{'name': topic.strip()} for topic in row[csv_column_headers.DATASET_TOPICS].split(';')]),
                'extras': [ # custom fields
                  {
                    'key': 'Data type',
                    'value': row[csv_column_headers.DATASET_TYPE]
                  },
                  {
                    'key': 'Method of access',
                    'value': row[csv_column_headers.DATASET_TRANSFER_METHOD]
                  },
                  {
                    'key': 'Volume',
                    'value': row[csv_column_headers.DATASET_VOLUME]
                  },
                  {
                    'key': 'Frequency of change',
                    'value': row[csv_column_headers.DATASET_CHANGE_FREQUENCY]
                  },
                  {
                    'key': 'Data Owner',
                    'value': row[csv_column_headers.DATASET_DATA_OWNER]
                  },
                  {
                    'key': 'Data agreements',
                    'value': row[csv_column_headers.DATASET_DATA_AGREEMENTS]
                  },
                  {
                    'key': 'Status',
                    'value': row[csv_column_headers.DATASET_STATUS]
                  },
                  {
                    'key': 'Contact',
                    'value': row[csv_column_headers.DATASET_CONTACT]
                  },
                  {
                    'key': 'Data Sharing Agreement Category',
                    'value': row[csv_column_headers.DATASET_VISIBILITY]
                  }         
                ]
            }
            import_dataset(dataset_dict)
            count += 1

    print(f'Imported {count} datasets.')

except Exception as err:
    print(err)
