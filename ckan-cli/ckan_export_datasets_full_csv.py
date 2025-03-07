'''
Exports full dataset list to CSV from a CKAN instance via the API.
Outputs data to a .csv file.
'''

import requests
import argparse
import traceback
from datetime import datetime
import csv

date = datetime.now().strftime("%d-%m-%Y")

parser = argparse.ArgumentParser("ckan_export_datasets_full_csv", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--ckan_url", dest="ckan_url", help="Target CKAN instance.", default="http://localhost:5000", type=str)
parser.add_argument("--api_key", dest="api_key", help="CKAN API Key with necessary read permissions", type=str, required=True)
parser.add_argument("--output_file", dest="output_file", help="Output path for csv file", default=f"sample_data/Exports/{date}.csv", type=str)
parser.add_argument("--limit", dest="limit", help="Maximum number of datasets to export", default=1000, type=int)
args = parser.parse_args()

def get_datasets():
    # Gets list of all datasets with all fields.
    url = f'{args.ckan_url}/api/action/current_package_list_with_resources?limit={args.limit}'

    # provide API key from your user account on the CKAN site that you're creating the dataset on.
    payload = {}
    files={}
    headers = {
        'Authorization': args.api_key,
    }
    
    try:
        response = requests.request("GET", url, headers=headers, data=payload, files=files, verify=False)
        if response.status_code == 200:
            response_dict = response.json()
            if response_dict['success'] == True:
                parse_datasets(response_dict['result'])

        else:
            raise Exception(f'get_datasets(): failed to get datasets. {response.status_code}')

    except requests.exceptions.HTTPError as err:
        raise Exception(f'get_datasets(): failed to get datasets. {err}')
    except requests.exceptions.RequestException as err:
        raise Exception(f'get_datasets(): error {err}')

def join_topics(topics):
    return '; '.join([topic['name'] for topic in topics])

def join_resources(resources):
    name_list = '; '.join([resource['name'] for resource in resources])
    url_list = '; '.join([resource['url'] for resource in resources])
    format_list = '; '.join([resource['format'] for resource in resources])
    desc_list = '; '.join([resource['description'] for resource in resources])
    cat_list = '; '.join([data_category_lookup(int(resource['resource_data_category'])) for resource in resources])
    acc_list = '; '.join(resource.get('resource_data_access', "Unassigned") for resource in resources)
    
    resource_list = {'name': name_list, 'url': url_list, 
                        'format': format_list, 'description': desc_list,
                        'resource_data_category': cat_list,
                        'resource_data_access': acc_list}
    return resource_list

def data_category_lookup(category):
    data_categories = {
        0: "Open",
        1: "Controlled",
        2: "Controlled (Personal Info)",
        3: "Confidential"
    }
    return data_categories.get(category)

def parse_datasets(datasets: dict):
    with open(args.output_file, mode='a', newline='') as csv_file:
        for dataset in datasets:
            topics = join_topics(dataset['groups'])
            resources = join_resources(dataset['resources'])
            dataset_dict = {
                    'Name': dataset['name'],
                    'Title': dataset['title'],
                    'Source': dataset['organization']['title'],
                    'Publisher': dataset['organization']['name'],
                    'Data agreements': dataset['license_title'],
                    'License': dataset['license_id'],
                    'Data owners': dataset.get('data_owners'),
                    'Data stewards': dataset.get('data_stewards'),
                    "Data quality score": dataset.get('data_quality_score'),
                    "Date created": dataset.get('metadata_created'),
                    "Last modified": dataset.get('metadata_modified'),
                    "Last reviewed": dataset.get('last_reviewed'),
                    'Description': dataset['notes'] or "No description provided",
                    'Dataset visibility': "Private" if dataset['private'] else "Public",
                    'Tags': dataset['tags'] or "",
                    'Topics': topics,
                    'Resource title': resources.get('name'),
                    'Resource description': resources.get('description'),
                    'Resource url': resources.get('url'),
                    'Resource format': resources.get('format'),
                    'Resource data category': resources.get('resource_data_category'),
                    'Resource data access': resources.get('resource_data_access')
                }

            writer = csv.DictWriter(csv_file, fieldnames=dataset_dict.keys())

            if csv_file.tell() == 0:
                writer.writeheader()
    
            writer.writerow(dataset_dict)

try:
   get_datasets()
   print(f'Exported data to {args.output_file}')

except Exception:
    print(traceback.format_exc())
