'''
Imports CKAN datasets from a Zip file via the CKAN API.
'''

import requests
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
        # CKAN package_create function creates a new dataset.
        url = f'{args.ckan_url}/api/action/package_create'

        payload = dataset
        files={}
        headers = {
          'Authorization': args.api_key,
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            if response.status_code == 200:
                count += 1
            else:
                raise Exception(f'import_datasets(): failed to create dataset(s). {response.status_code}')

        except requests.exceptions.HTTPError as err:
            if response.status_code == 200:
                raise Exception(f'import_datasets(): data conflict in row {dataset}')
            raise Exception(f'import_datasets(): failed to import dataset. {err}')
        except requests.exceptions.RequestException:
            raise Exception(f'import_datasets(): invalid URL')
        
    return count

try:
    json_files = get_json_files_from_zip(args.zipfile)
    print('Running...')

    dataset_count = import_datasets(json_files[tdh_package.DATASETS_FILENAME])
    print(f'Imported {dataset_count} Datasets')

except Exception as err:
    print(err)
