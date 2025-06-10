'''
Imports CKAN datasets from a JSON ZIP file via the CKAN API.
'''

from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import URLError, HTTPError
import argparse
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
        except HTTPError as err:
            # check for data conflict
            if err.code == 409:
                print(f'import_datasets(): data conflict in {dataset.get("name")}, attempting update...')
                update_dataset(dataset)
            else:
                raise Exception(f'import_datasets(): failed to import dataset. {err}')
        except URLError:
            raise Exception(f'import_datasets(): invalid URL')

        count += 1
    return count

def update_dataset(dataset):
    data_string = quote(json.dumps(dataset)).encode('utf-8')
    request = Request(f'{args.ckan_url}/api/action/package_update')
    request.add_header('Authorization', args.api_key)

    # Make the HTTP request to update the dataset.
    try:
        urlopen(request, data_string)
        print(f'update_dataset(): successfully updated dataset {dataset.get("name")}')
    except HTTPError as err:
        raise Exception(f'import_datasets(): failed to update dataset. {err}')
    except URLError:
        raise Exception(f'import_datasets(): invalid URL')

try:
    json_files = get_json_files_from_zip(args.zipfile)
    print('Running...')

    dataset_count = import_datasets(json_files[tdh_package.DATASETS_FILENAME])
    print(f'Imported {dataset_count} Datasets')

except Exception as err:
    print(err)
