'''
Updates a list of datasets from a CSV file via the CKAN API.
Requires necessary publishers and topics to have been created.
'''

import argparse
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import URLError, HTTPError
import csv
from datetime import datetime
import json
import csv_column_headers
import traceback

parser = argparse.ArgumentParser("create_datasets", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--filename", dest="filename", help="Input file path", type=str, required=True)
parser.add_argument("--ckan_url", dest="ckan_url", help="Target CKAN instance.", default="http://localhost:5000", type=str)
parser.add_argument("--api_key", dest="api_key", help="API Key with necessary write permissions", type=str, required=True)
args = parser.parse_args()
count = 0

def seperate_resources(row):
    resources = []
  
    name_list = [resource.strip() for resource in row[csv_column_headers.RESOURCE_TITLE].split(';')]
    desc_list = [resource.strip() for resource in row[csv_column_headers.RESOURCE_DESCRIPTION].split(';')]
    url_list = [resource.strip() for resource in row[csv_column_headers.RESOURCE_URL].split(';')]
    format_list = [resource.strip() for resource in row[csv_column_headers.RESOURCE_FORMAT].split(';')]
    category_list = [resource.strip() for resource in row[csv_column_headers.RESOURCE_DATA_CATEGORY].split(';')]
    access_list = [resource.strip() for resource in row[csv_column_headers.RESOURCE_DATA_ACCESS_TYPE].split(';')]
    date_list = [resource.strip() for resource in row[csv_column_headers.RESOURCE_DATE_CREATED].split(';')]
    
    for i in range(0, len(name_list)):
      resources.append({'name': name_list[i], 'url': url_list[i], 
                         'format': format_list[i], 'description': desc_list[i],
                         'resource_data_category': data_category_lookup(category_list[i]),
                         'resource_data_access': access_list[i],
                         'created': date_list[i]})
    
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

def update_dataset(dataset_dict):
    global count
    
    # Use the json module to dump the dictionary to a string for posting. URL encode.
    data_string = quote(json.dumps(dataset_dict)).encode('utf-8')
    
    # Update package
    request = Request(f'{args.ckan_url}/api/action/package_update')

    # Creating a dataset requires an authorization header.
    # provide API key from your user account on the CKAN site that you're creating the dataset on.
    request.add_header('Authorization', args.api_key)

    # Make the HTTP request.
    try:
        urlopen(request, data_string)
        print(f"Updating dataset {row['Title']}...")
        count += 1
    except HTTPError as err:
        if err.code == 409:
            raise Exception(f'update_dataset(): data conflict in row {row}')
        elif err.code == 404:
            raise Exception(f'update_dataset(): dataset {row["Title"]} does not exist')
        raise Exception(f'update_dataset(): failed to update dataset. {err}')
    except URLError:
        raise Exception('update_dataset(): invalid URL')
    
    return count

try:
    with open(args.filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        print("Running...")

        for row in reader:
            # map the details of the dataset to create to a dict
            dataset_dict = {
                'name': row[csv_column_headers.DATASET_NAME], # required
                'title': row[csv_column_headers.DATASET_TITLE],
                'owner_org': row[csv_column_headers.DATASET_PUBLISHER],
                'license_id': row[csv_column_headers.DATASET_LICENSE],
                'notes': row[csv_column_headers.DATASET_NOTES] or "No description provided",
                'private': False if row[csv_column_headers.DATASET_VISIBILITY] else True,
                'tags': [] if not row[csv_column_headers.DATASET_TAGS] else list([{'name': tag.strip()} for tag in row[csv_column_headers.DATASET_TAGS].split(';')]),
                'groups': [] if not row[csv_column_headers.DATASET_TOPICS] else list([{'name': topic.strip()} for topic in row[csv_column_headers.DATASET_TOPICS].split(';')]),
                'resources': seperate_resources(row),
                'data_owners': row[csv_column_headers.DATASET_DATA_OWNERS],
                'data_stewards': row[csv_column_headers.DATASET_DATA_STEWARDS],
                'last_reviewed': row[csv_column_headers.DATASET_LAST_REVIEWED],
                'data_quality': data_quality_lookup(row[csv_column_headers.DATASET_DATA_QUALITY_CATEGORY]),
                'data_quality_score': row[csv_column_headers.DATASET_DATA_QUALITY_SCORE]
            }
            update_dataset(dataset_dict)

    print(f'Updated {count} datasets.')

except Exception:
    print(traceback.format_exc())
