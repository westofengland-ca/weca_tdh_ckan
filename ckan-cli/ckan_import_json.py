'''
Imports CKAN data from a Zip file via the CKAN API.
'''

import argparse
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import URLError, HTTPError
import json
import zipfile
import tdh_package

parser = argparse.ArgumentParser("create_datasets", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--zipfile", dest="zipfile", help="Input zip file path", type=str, required=True)
parser.add_argument("--ckan_url", dest="ckan_url", help="Target CKAN instance", default="http://localhost:5000", type=str)
parser.add_argument("--api_key", dest="api_key", help="API Key with necessary write permissions", type=str, required=True)
args = parser.parse_args()

def get_json_files_from_zip(zip_path):
    json_files = {}

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            if file_info.filename.endswith('.json'):
                with zip_ref.open(file_info.filename) as json_file:
                    data = json_file.read()
                    json_data = json.loads(data)
                    json_files[file_info.filename] = json_data
    return json_files

def import_publishers(publishers):
    count = 0
    for publisher in publishers:
        # Use the json module to dump the dictionary to a string for posting. URL encode.
        data_string = quote(json.dumps(publisher)).encode('utf-8')

        # CKAN package_create function creates a new dataset.
        request = Request(f'{args.ckan_url}/api/action/organization_create')

        # Creating a dataset requires an authorization header.
        # provide API key from your user account on the CKAN site that you're creating the dataset on.
        request.add_header('Authorization', args.api_key)

        # Make the HTTP request.
        try:
            urlopen(request, data_string)
            count += 1
        except HTTPError as err:
            if err.code == 409:
                raise Exception(f'import_publishers(): data conflict in row {publisher}')
            raise Exception(f'import_publishers(): failed to import publisher. {err}')
        except URLError as err:
            raise Exception(f'import_publishers(): invalid URL. {err}')
        
    return count

def import_topics(topics):
    count = 0
    for topic in topics:
        # Use the json module to dump the dictionary to a string for posting. URL encode.
        data_string = quote(json.dumps(topic)).encode('utf-8')

        # CKAN package_create function creates a new dataset.
        request = Request(f'{args.ckan_url}/api/action/group_create')

        # Creating a dataset requires an authorization header.
        # provide API key from your user account on the CKAN site that you're creating the dataset on.
        request.add_header('Authorization', args.api_key)

        # Make the HTTP request.
        try:
            urlopen(request, data_string)
            count += 1
        except HTTPError as err:
            if err.code == 409:
                raise Exception(f'import_topics(): data conflict in row {topic}')
            raise Exception(f'import_topics(): failed to import topic. {err}')
        except URLError as err:
            raise Exception(f'import_topics(): invalid URL. {err}')
            
    return count

def import_datasets(datasets):
    count = 0
    for dataset in datasets:
        # Use the json module to dump the dictionary to a string for posting. URL encode.
        data_string = quote(json.dumps(dataset)).encode('utf-8')

        # CKAN package_create function creates a new dataset.
        request = Request(f'{args.ckan_url}/api/action/package_create')

        # Creating a dataset requires an authorization header.
        # provide API key from your user account on the CKAN site that you're creating the dataset on.
        request.add_header('Authorization', args.api_key)

        # Make the HTTP request.
        try:
            urlopen(request, data_string)
            count += 1
        except HTTPError as err:
            if err.code == 409:
                raise Exception(f'import_datasets(): data conflict in row {dataset}')
            raise Exception(f'import_datasets(): failed to import dataset. {err}')
        except URLError as err:
            raise Exception(f'import_datasets(): invalid URL {err}')
        
    return count

try:
    json_files = get_json_files_from_zip(args.zipfile)
    print('Running...')

    pub_count = import_publishers(json_files[tdh_package.PUBLISHERS_FILENAME])
    print(f'Imported {pub_count} Publishers')

    topic_count = import_topics(json_files[tdh_package.TOPICS_FILENAME])
    print(f'Imported {topic_count} Topics')

    dataset_count = import_datasets(json_files[tdh_package.DATASETS_FILENAME])
    print(f'Imported {dataset_count} Datasets')

except Exception as err:
    print(err)
