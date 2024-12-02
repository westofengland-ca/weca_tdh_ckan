import ckanext.weca_tdh.config as C
from datetime import datetime

def filter_datetime(string: str, format: str = 'full') -> str:
    try:
        dt = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%f')   

    except (ValueError, TypeError):
        try:
            dt = datetime.strptime(string, '%Y-%m-%d')
        except:
            return ""

    if format == 'short':
        return dt.strftime('%d %b %Y')      
 
    return dt.strftime('%d %b %Y %H:%M:%S')

def get_cookie_control_config() -> dict:
    cookie_control_config = {}

    api_key = C.CCC_API_KEY
    cookie_control_config['api_key'] = api_key

    license_type = C.CCC_LICENSE
    cookie_control_config['license_type'] = license_type

    return cookie_control_config

def get_google_analytics_config() -> dict:
    google_analytics_config = {}

    ga_id = C.GA_ID
    google_analytics_config['ga_id'] = ga_id

    return google_analytics_config

def get_resource_data_categories() -> list:
    data_categories = [{
        "id": 0,
        "name": "Open",
        "desc": "Can be accessed by anyone (with access to the TDH).",
        "class": "data-category-open"
      },
      {
        "id": 1,
        "name": "Controlled",
        "desc": "Can be accessed by defined teams or persons.",
        "class": "data-category-cont"
      },
      {
        "id": 2,
        "name": "Controlled (Personal Info)",
        "desc": "Subject to GDPR; only accessible by relevant teams or persons.",
        "class": "data-category-contpi"
      },
      {
        "id": 3,
        "name": "Confidential",
        "class": "data-category-con"
    }]

    return data_categories

def get_data_quality_markings() -> list:
    data_quality_markings = [{
        "id": 0,
        "name": "Unclassified",
        "score": "Unclassified",
      },
      {
        "id": 1,
        "name": "Poor",
        "score": "<45",
      },
      {
        "id": 2,
        "name": "Moderate",
        "score": "45-54",
      },
      {
        "id": 3,
        "name": "Good",
        "score": "55-64",
      },
      {
        "id": 4,
        "name": "Excellent",
        "score": "65-76",
    }]

    return data_quality_markings

def sort_file_formats(filter_items: list) -> list:  
    sorted_items = []

    # Set to track seen values
    seen_values = set()

    for item in filter_items:
        if ',' in item['value']:
            # Split the comma-separated values
            values = item['value'].split(', ')
            for value in values:
                if value not in seen_values:
                    # Add the value to the seen set
                    seen_values.add(value)
                    # Create new entries for each unique value
                    sorted_items.append({'value': value, 'text': value, 'selected': item.get('selected', 'Undefined')})
        else:
            if item['value'] not in seen_values:
                # Add the value to the seen set
                seen_values.add(item['value'])
                # Keep the entry as is
                sorted_items.append(item)
    
    return sorted_items

def sort_custom_metadata(page_items: list, current_filter: str) -> list:  
    sorted_items = [{'value': "", 'text': ""}]

    # Set to track seen values
    seen_values = set()
    
    for item in page_items:
        for extra in item.get('extras'):
            value = extra.get('value')
            if extra.get('key') == 'parent_org' and value and value not in seen_values:
                # Add the value to the seen set
                seen_values.add(value)
                 
                # Create new entries for each unique value
                sorted_items.append({
                    'value': value, 
                    'text': value,
                    'selected': value == current_filter
                })
    
    return sorted_items
