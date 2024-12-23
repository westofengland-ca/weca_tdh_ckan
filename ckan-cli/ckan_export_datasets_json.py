'''
Exports datasets by name or id from a CKAN instance via the API.
Outputs data to a .json file, zipped up.
'''

import requests
import argparse
from datetime import datetime
import getpass
import json
import zipfile
import io
import tdh_package
from tkinter.filedialog import askopenfilename

parser = argparse.ArgumentParser("ckan_export_datasets_json", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--ckan_url", dest="ckan_url", help="Target CKAN instance.", default="http://localhost:5000", type=str)
parser.add_argument("--api_key", dest="api_key", help="CKAN API Key with necessary read permissions", type=str, required=True)
parser.add_argument("--output_file", dest="output_file", help="Output path for zip file", default="sample_data/ckan-export/ckan-export.zip", type=str)
args = parser.parse_args()

def get_info():
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    export_info = {
        'name': tdh_package.PACKAGE_NAME,
        'version': tdh_package.VERSION_NO,
        'user': getpass.getuser(),
        'created': dt_string,
        'CKAN_URL': args.ckan_url
    }

    info_file = io.BytesIO(json.dumps(export_info).encode())
    return info_file.getvalue()

def get_datasets(filepath):
    datasets = open(filepath, 'r')
    Lines = datasets.readlines()
    datasets = []

    # Strips the newline character
    for line in Lines:
        url = f"{args.ckan_url}/api/action/package_show?id={line.strip()}"

        payload = {}
        files={}
        headers = {
          'Authorization': args.api_key,
        }

        try:
            response = requests.request("GET", url, headers=headers, data=payload, files=files)
            if response.status_code == 200:
                response_dict = response.json()
                if response_dict['success'] == True:
                  datasets.append(response_dict['result'])

            else:
                raise Exception(f'get_datasets(): failed to get datasets. {response.status_code}')

        except requests.exceptions.HTTPError as err:
            raise Exception(f'get_datasets(): failed to get datasets. {err}')
        except requests.exceptions.RequestException:
            raise Exception(f'get_datasets(): invalid URL')
        
    datasets_file = io.BytesIO(json.dumps(datasets).encode())
    return datasets_file.getvalue()

try:
    print("Choose input file...")
    filepath = askopenfilename()

    with io.BytesIO() as zip_buffer:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr(tdh_package.INFO_FILENAME, get_info())
            zipf.writestr(tdh_package.DATASETS_FILENAME, get_datasets(filepath))

        with open(args.output_file, 'wb') as output_zip:
            output_zip.write(zip_buffer.getvalue())

        print(f'Exported data to {args.output_file}')

except Exception as err:
    print(err)
