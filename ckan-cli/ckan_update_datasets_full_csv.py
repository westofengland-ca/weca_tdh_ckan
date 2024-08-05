'''
Updates a list of datasets from a CSV file via the CKAN API.
Requires necessary publishers and topics to have been created.
'''

import argparse
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import URLError, HTTPError
import csv
import json
import csv_column_headers

parser = argparse.ArgumentParser("create_datasets", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--filename", dest="filename", help="Input file path", type=str, required=True)
parser.add_argument("--ckan_url", dest="ckan_url", help="Target CKAN instance.", default="http://localhost:5000", type=str)
parser.add_argument("--api_key", dest="api_key", help="API Key with necessary write permissions", type=str, required=True)
args = parser.parse_args()

def seperate_resources(row):
    resources = []
  
    name_list = [resource.strip() for resource in row['Resource title'].split(';')]
    url_list = [resource.strip() for resource in row['Resource url'].split(';')]
    format_list = [resource.strip() for resource in row['Resource format'].split(';')]
    desc_list = [resource.strip() for resource in row['Resource description'].split(';')]
    cat_list = [resource.strip() for resource in row['Resource data category'].split(';')]
    
    for i in range(0, len(name_list)):
      resources.append({'name': name_list[i], 'url': url_list[i], 
                         'format': format_list[i], 'description': desc_list[i],
                         'resource_data_category': cat_list[i]})
    
    return resources

def update_dataset(dataset_dict):
    # Use the json module to dump the dictionary to a string for posting. URL encode.
    data_string = quote(json.dumps(dataset_dict)).encode('utf-8')

    # CKAN package_create function creates a new dataset.
    request = Request(f'{args.ckan_url}/api/action/package_update')

    # Creating a dataset requires an authorization header.
    # provide API key from your user account on the CKAN site that you're creating the dataset on.
    request.add_header('Authorization', args.api_key)

    # Make the HTTP request.
    try:
        urlopen(request, data_string)
        print(f"Updating dataset {row['Title']}...")
    except HTTPError as err:
        if err.code == 409:
            raise Exception(f'update_dataset(): data conflict in row {row}')
        elif err.code == 404:
            raise Exception(f'update_dataset(): dataset {row["Title"]} does not exist')
        raise Exception(f'update_dataset(): failed to update dataset. {err}')
    except URLError:
        raise Exception(f'update_dataset(): invalid URL')

try:
    with open(args.filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        print("Running...")

        for row in reader:  
            # map the details of the dataset to create to a dict
            dataset_dict = {
                'name': row['Name'], # required
                'title': row['Title'],
                'owner_org': row['Publisher'], # Publisher
                'private': False if row['Dataset visibility'] else True,
                'license_id': row['License'],
                'notes': row[csv_column_headers.DATASET_DESC] or "No description provided",
                'resources': seperate_resources(row),
                'groups': [] if not row[csv_column_headers.DATASET_TOPICS] else list([{'name': topic.strip()} for topic in row[csv_column_headers.DATASET_TOPICS].split(';')]),
                'datalake_active': row['Datalake'],
            }
            update_dataset(dataset_dict)
            count += 1

    print(f'Updated {count} datasets.')

except Exception as err:
    print(err)
