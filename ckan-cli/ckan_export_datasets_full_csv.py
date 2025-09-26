'''
Exports full dataset list to CSV from a CKAN instance via the API.
Outputs data to a .csv file.
'''

import argparse
import csv
import traceback
from datetime import datetime

import csv_column_headers as head
import requests

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
    payload = {}
    files={}
    headers = {
        'Authorization': args.api_key,
    }
    
    try:
        response = requests.request("GET", url, headers=headers, data=payload, files=files, verify=False)
        if response.status_code == 200:
            response_dict = response.json()
            if response_dict['success']:
                parse_datasets(response_dict['result'])

        else:
            raise Exception(f'get_datasets(): failed to get datasets. {response.status_code}')

    except requests.exceptions.HTTPError as err:
        raise Exception(f'get_datasets(): failed to get datasets. {err}')
    except requests.exceptions.RequestException as err:
        raise Exception(f'get_datasets(): error {err}')


def join_tags(tags):
    return '; '.join([tag['display_name'] for tag in tags])


def join_topics(topics):
    return '; '.join([topic['name'] for topic in topics])


def join_list_items(items):
    return '; '.join([str(item) for item in items])


def join_resources(resources):
    def join_field(key, default="", transform=lambda v: v, condition=lambda r: True):
        values = [
            transform(r.get(key, default))
            for r in resources
            if condition(r) and r.get(key, default) is not None
        ]
        return "; ".join(values)

    return {
        "name": join_field("name"),
        "url": join_field("url"),
        "format": join_field("format"),
        "description": join_field("description"),
        "resource_data_category": join_field(
            "resource_data_category",
            transform=lambda v: data_category_lookup(int(v)),
        ),
        "resource_data_access": join_field("resource_data_access"),
        "created": join_field("created"),
        "tdh_catalog": join_field(
            "tdh_catalog",
            condition=lambda r: r.get("resource_data_access") in ("Power BI Report", "TDH Query"),
        ),
        "tdh_table": join_field(
            "tdh_table",
            condition=lambda r: r.get("resource_data_access") == "TDH Query",
        ),
    }


def data_category_lookup(category):
    data_categories = {
        0: "Open",
        1: "Controlled",
        2: "Controlled (Personal Info)",
        3: "Confidential"
    }
    return data_categories.get(category)


def data_quality_lookup(quality):
    data_quality_categories = {
        0: "Unclassified",
        1: "Poor",
        2: "Moderate",
        3: "Good",
        4: "Excellent"
    }
    return data_quality_categories.get(quality)


def parse_datasets(datasets: dict):
    sorted_datasets = sorted(datasets, key=lambda x: x['title'])

    with open(args.output_file, mode='a', newline='') as csv_file:
        for dataset in sorted_datasets:
            resources = join_resources(dataset['resources'])
            dataset_dict = {
                head.DATASET_NAME: dataset['name'],
                head.DATASET_TITLE: dataset['title'],
                head.DATASET_SOURCE: dataset['organization']['title'],
                head.DATASET_PUBLISHER: dataset['organization']['name'],
                head.DATASET_DATA_AGREEMENTS: dataset['license_title'],
                head.DATASET_LICENSE: dataset['license_id'],
                head.DATASET_NOTES: dataset['notes'] or 'No description provided',
                head.DATASET_AVAILABILITY: dataset.get('availability', 'available'),
                head.DATASET_VISIBILITY: 'Private' if dataset['private'] else 'Public',
                head.DATASET_FEATURED: dataset.get('featured', False),
                head.DATASET_TAGS: join_tags(dataset.get('tags', [])),
                head.DATASET_TOPICS: join_topics(dataset.get('groups', [])),
                head.RESOURCE_TITLE: resources.get('name'),
                head.RESOURCE_DESCRIPTION: resources.get('description'),
                head.RESOURCE_URL: resources.get('url'),
                head.RESOURCE_FORMAT: resources.get('format'),
                head.RESOURCE_DATA_CATEGORY: resources.get('resource_data_category'),
                head.RESOURCE_DATA_ACCESS_TYPE: resources.get('resource_data_access'),
                head.RESOURCE_DATE_CREATED: resources.get('created'),
                head.RESOURCE_TDH_CATALOG: resources.get('tdh_catalog'),
                head.RESOURCE_TDH_TABLE: resources.get('tdh_table'),
                head.DATASET_DATA_OWNERS: dataset.get('data_owners', ['Unassigned']),
                head.DATASET_DATA_STEWARDS: dataset.get('data_stewards', ['Unassigned']),
                head.DATASET_DATE_CREATED: dataset.get('metadata_created'),
                head.DATASET_LAST_MODFIED: dataset.get('metadata_modified'),
                head.DATASET_LAST_REVIEWED: dataset.get('last_reviewed'),
                head.DATASET_DATA_QUALITY_CATEGORY: data_quality_lookup(int(dataset.get('data_quality', 0))),
                head.DATASET_DATA_QUALITY_SCORE: dataset.get('data_quality_score'),
                head.DATASET_USER_GROUP: dataset.get('user_group')
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
