'''
Exports organisations, groups and datasets + resources from a CKAN instance via the API.
Outputs data to three seperate .json files, zipped up.
'''

import argparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import datetime
import getpass
import json
import zipfile
import io
import common

parser = argparse.ArgumentParser("ckan_export", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--ckan_url", dest="ckan_url", help="Target CKAN instance.", default="http://localhost:5000", type=str)
parser.add_argument("--api_key", dest="api_key", help="CKAN API Key with necessary read permissions", type=str, required=True)
parser.add_argument("--output_file", dest="output_file", help="Output path for zip file", default="ckan-export.zip", type=str)
parser.add_argument("--limit", dest="limit", help="Maximum number of datasets to export", default=1000, type=int)
args = parser.parse_args()

def get_info():
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    export_info = {
        'name': 'CKAN export - json',
        'user': getpass.getuser(),
        'created': dt_string,
        'CKAN_URL': args.ckan_url
    }

    info_file = io.BytesIO(json.dumps(export_info).encode())
    return info_file.getvalue()

def get_datasets():
    # Gets list of all datasets with all fields.
    request = Request(f'{args.ckan_url}/api/action/current_package_list_with_resources?limit={args.limit}')

    # provide API key from your user account on the CKAN site that you're creating the dataset on.
    request.add_header('Authorization', args.api_key)

    # Make the HTTP request.
    try:
        response = urlopen(request)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        datasets = response_dict['result']
        datasets_file = io.BytesIO(json.dumps(datasets).encode())
        return datasets_file.getvalue()      

    except HTTPError as err:
        print(err)

def get_publishers():
    # Gets list of all organisations with all fields.
    request = Request(f'{args.ckan_url}/api/action/organization_list?all_fields=true')

    # provide API key from your user account on the CKAN site that you're creating the dataset on.
    request.add_header('Authorization', args.api_key)

    # Make the HTTP request.
    try:
        response = urlopen(request)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        publishers = response_dict['result']
        publishers_file = io.BytesIO(json.dumps(publishers).encode())
        return publishers_file.getvalue()

    except HTTPError as err:
        print(err)

def get_topics():
    # Gets list of all groups with all fields.
    request = Request(f'{args.ckan_url}/api/action/group_list?all_fields=true')

    # provide API key from your user account on the CKAN site that you're creating the dataset on.
    request.add_header('Authorization', args.api_key)

    # Make the HTTP request.
    try:
        response = urlopen(request)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True
    
        topics = response_dict['result']
        topics_file = io.BytesIO(json.dumps(topics).encode())
        return topics_file.getvalue()

    except HTTPError as err:
        print(err)

with io.BytesIO() as zip_buffer:
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(common.FILENAMES['info'], get_info())
        zipf.writestr(common.FILENAMES['datasets'], get_datasets())
        zipf.writestr(common.FILENAMES['publishers'], get_publishers())
        zipf.writestr(common.FILENAMES['topics'], get_topics())

    #zip_path = args.output_file or 'ckan-export.zip'
    with open(args.output_file, 'wb') as output_zip:
        output_zip.write(zip_buffer.getvalue())
