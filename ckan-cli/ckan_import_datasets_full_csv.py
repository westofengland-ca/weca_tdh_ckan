'''
Imports a list of datasets from a CSV file via the CKAN API.
Requires necessary publishers and topics to have been created.
'''

import argparse
import csv
import json
import traceback
from datetime import datetime
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

import csv_column_headers as head

parser = argparse.ArgumentParser("create_datasets", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--filename", dest="filename", help="Input file path", type=str, required=True)
parser.add_argument("--ckan_url", dest="ckan_url", help="Target CKAN instance.", default="http://localhost:5000", type=str)
parser.add_argument("--api_key", dest="api_key", help="API Key with necessary write permissions", type=str, required=True)
args = parser.parse_args()
count = 0


def separate_resources(row):
    field_map = {
        "name": head.RESOURCE_TITLE,
        "description": head.RESOURCE_DESCRIPTION,
        "url": head.RESOURCE_URL,
        "format": head.RESOURCE_FORMAT,
        "resource_data_category": head.RESOURCE_DATA_CATEGORY,
        "resource_data_access": head.RESOURCE_DATA_ACCESS_TYPE,
        "created": head.RESOURCE_DATE_CREATED,
        "tdh_catalog": head.RESOURCE_TDH_CATALOG,
        "tdh_table": head.RESOURCE_TDH_TABLE,
    }

    split_fields = {
        key: [value.strip() for value in row[col].split(";") if value.strip()]
        for key, col in field_map.items()
    }

    # Ensure all lists have the same length
    max_len = max(len(values) for values in split_fields.values())
    for key, values in split_fields.items():
        if len(values) < max_len:
            values.extend([""] * (max_len - len(values)))

    resources = []
    for i in range(max_len):
        resource = {key: values[i] for key, values in split_fields.items()}
        resource["resource_data_category"] = data_category_lookup(resource["resource_data_category"])
        resources.append(resource)

    return resources


def data_category_lookup(category):
    data_categories = {
        "Open": "0",
        "Controlled": "1",
        "Controlled (Personal Info)": "2",
        "Confidential": "3"
    }
    return data_categories.get(category)


def data_quality_lookup(quality):
    data_quality_categories = {
        "Unclassified": "0",
        "Poor": "1",
        "Moderate": "2",
        "Good": "3",
        "Excellent": "4"
    }
    return data_quality_categories.get(quality)


def convert_date_format(date_str):
    if date_str:
        date_str = datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
    return date_str


def import_dataset(dataset_dict):
    global count
    
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
        print(f"Imported dataset {row["Title"]}.")
        count += 1
    except HTTPError as err:
        if err.code == 409:
            print(f"Dataset {row["Title"]} already exists. Skipping...")
        else:
            raise Exception(f'import_dataset(): failed to import dataset. {err}')
    except Exception as err:
        raise Exception(f'import_dataset(): {row["Title"]} failed. {err}')
    
    return count

try:
    with open(args.filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        print("Running...")

        for row in reader:  
            # map the details of the dataset to create to a dict
            dataset_dict = {
                'name': row[head.DATASET_NAME], # required
                'title': row[head.DATASET_TITLE],
                'owner_org': row[head.DATASET_PUBLISHER],
                'license_id': row[head.DATASET_LICENSE],
                'notes': row[head.DATASET_NOTES] or "No description provided",
                'availability': row[head.DATASET_AVAILABILITY],
                'private': False if row[head.DATASET_VISIBILITY] == 'Public' else True,
                'featured': row[head.DATASET_FEATURED],
                'tags': [] if not row[head.DATASET_TAGS] else list([{'name': tag.strip()} for tag in row[head.DATASET_TAGS].split(';')]),
                'groups': [] if not row[head.DATASET_TOPICS] else list([{'name': topic.strip()} for topic in row[head.DATASET_TOPICS].split(';')]),
                'resources': separate_resources(row),
                'data_owners': row[head.DATASET_DATA_OWNERS],
                'data_stewards': row[head.DATASET_DATA_STEWARDS],
                'last_reviewed': row[head.DATASET_LAST_REVIEWED],
                'data_quality': data_quality_lookup(row[head.DATASET_DATA_QUALITY_CATEGORY]),
                'data_quality_score': row[head.DATASET_DATA_QUALITY_SCORE],
                'user_group': row[head.DATASET_USER_GROUP]
            }
            import_dataset(dataset_dict)

    print(f'Imported {count} datasets.')

except Exception:
    print(traceback.format_exc())
