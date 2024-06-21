import ckanext.weca_tdh.config as C
from datetime import datetime

def filter_datetime(string, format='full') -> str:   
    try:
        dt = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%f')   
    except (ValueError, TypeError):
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
        "desc": "Can be accessed by anyone.",
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
        "desc": "Subject to GDPR; can only be accessed by relevant teams or persons.",
        "class": "data-category-contpi"
      },
      {
        "id": 3,
        "name": "Confidential",
        "class": "data-category-con"
    }]

    return data_categories
