import ckanext.weca_tdh.config as C
from datetime import datetime

def filter_datetime(string, format='full'):   
    try:
        dt = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%f')   
    except (ValueError, TypeError):
        return ""
    if format == 'short':
        return dt.strftime('%d %b %Y')        
    return dt.strftime('%d %b %Y %H:%M:%S')

def get_cookie_control_config():
    cookie_control_config = {}

    api_key = C.CCC_API_KEY
    cookie_control_config['api_key'] = api_key

    license_type = C.CCC_LICENSE
    cookie_control_config['license_type'] = license_type

    return cookie_control_config

def get_google_analytics_config():
    google_analytics_config = {}

    ga_id = C.GA_ID
    google_analytics_config['ga_id'] = ga_id

    return google_analytics_config
