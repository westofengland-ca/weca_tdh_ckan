'''
Imports a list of publishers from a CSV file via the CKAN API.
'''

import argparse
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import URLError, HTTPError
import csv
import json
import csv_column_headers

parser = argparse.ArgumentParser("create_publishers", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--filename", dest="filename", help="Input file path", type=str, required=True)
parser.add_argument("--ckan_url", dest="ckan_url", help="Target CKAN instance.", default="http://localhost:5000", type=str)
parser.add_argument("--api_key", dest="api_key", help="API Key with necessary write permissions", type=str, required=True)
args = parser.parse_args()

def import_publisher(pub_dict):
    # Use the json module to dump the dictionary to a string for posting. URL encode.
    data_string = quote(json.dumps(pub_dict)).encode('utf-8')

    # create a new organisation
    request = Request(f'{args.ckan_url}/api/action/organization_create')

    # provide API key from your user account on the CKAN site that you're creating the dataset on.
    request.add_header('Authorization', args.api_key)

    # Make the HTTP request.
    try:
        urlopen(request, data_string)      
    except HTTPError as err:
        if err.code == 409:
            raise Exception(f'import_publisher(): data conflict in row {row}')
        raise Exception(f'import_publisher(): failed to import publisher. {err}')
    except URLError:
        raise Exception(f'import_publisher(): invalid URL')

try:
    with open(args.filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        print("Running...")

        for row in reader:
            publisher_dict = {
                'id': row[csv_column_headers.PUBLISHER_GUID],
                'name': row[csv_column_headers.PUBLISHER_SLUG],
                'title': row[csv_column_headers.PUBLISHER_TITLE],
                'description': row[csv_column_headers.PUBLISHER_DESC]
            }
            import_publisher(publisher_dict)
            count += 1

    print(f'Imported {count} Publishers.')

except Exception as err:
    print(err)
