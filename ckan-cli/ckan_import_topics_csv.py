'''
Imports a list of topics from a CSV file via the CKAN API.
'''

import argparse
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import URLError, HTTPError
import csv
import json
import csv_column_headers

parser = argparse.ArgumentParser("create_topics", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--filename", dest="filename", help="Input file path", type=str, required=True)
parser.add_argument("--ckan_url", dest="ckan_url", help="Target CKAN instance.", default="http://localhost:5000", type=str)
parser.add_argument("--api_key", dest="api_key", help="API Key with necessary write permissions", type=str, required=True)
args = parser.parse_args()
count = 0

def import_topic(topic_dict):
    global count
    
    # Use the json module to dump the dictionary to a string for posting. URL encode.
    data_string = quote(json.dumps(topic_dict)).encode('utf-8')

    # create a new group
    request = Request(f'{args.ckan_url}/api/action/group_create')

    # provide API key from your user account on the CKAN site that you're creating the dataset on.
    request.add_header('Authorization', args.api_key)

    # Make the HTTP request.
    try:
        urlopen(request, data_string)
        print(f"Imported topic {row["Title"]}.")
        count += 1
    except HTTPError as err:
        if err.code == 409:
            print(f"Topic {row["Title"]} already exists. Skipping...")
        else:
            raise Exception(f'import_topic(): failed to import topic. {err}')
    except URLError:
        raise Exception('import_topic(): invalid URL')

    return count

try:
    with open(args.filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        print("Running...")

        for row in reader:
            topic_dict = {
                'id': row[csv_column_headers.TOPIC_GUID],
                'name': row[csv_column_headers.TOPIC_SLUG],
                'title': row[csv_column_headers.TOPIC_TITLE],
                'description': row[csv_column_headers.TOPIC_DESC],
                'image_url': f"{args.ckan_url}/assets/images/topics/{row[csv_column_headers.TOPIC_LOGO]}"
            }
            import_topic(topic_dict)

    print(f'Imported {count} Topics.')

except Exception as err:
    print(err)
