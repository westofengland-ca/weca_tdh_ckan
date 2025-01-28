'''
Imports a list of datasets from a CSV file via the CKAN API.
Requires necessary publishers and topics to have been created.
'''

import argparse
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError
import csv
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
  
    name_list = [resource.strip() for resource in row['Resource title'].split(';')]
    url_list = [resource.strip() for resource in row['Resource url'].split(';')]
    format_list = [resource.strip() for resource in row['Resource format'].split(';')]
    desc_list = [resource.strip() for resource in row['Resource description'].split(';')]
    cat_list = [resource.strip() for resource in row['Resource data category'].split(';')]
    
    for i in range(0, len(name_list)):
      resources.append({'name': name_list[i], 'url': url_list[i], 
                         'format': format_list[i], 'description': desc_list[i],
                         'resource_data_category': data_category_lookup(cat_list[i])})
    
    return resources

def data_category_lookup(category):
    data_categories = {
        "Open": 0,
        "Controlled": 1,
        "Controlled (Personal Info)": 2,
        "Confidential": 3
    }
    return data_categories.get(category)

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
            import_dataset(dataset_dict)

    print(f'Imported {count} datasets.')

except Exception:
    print(traceback.format_exc())

