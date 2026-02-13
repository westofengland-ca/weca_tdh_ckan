import json
import logging
import re

import ckan.plugins.toolkit as toolkit

def strip_unsafe(value):
    if isinstance(value,list):
        return [v.replace(",","").strip() for v in  value]
    else:
        return value.replace(",","").strip().strip('"')

def default_if_missing(default_value):
    def validator(value):
        if value is toolkit.missing or not value:
            return default_value
        value = strip_unsafe(value)
        return value
    return validator

def insert_publisher(key, data, errors, context):
    try:
        value = data.get(key, None)
        
        if not value or value is toolkit.missing:
            pub_id = data.get(('owner_org',)) or data.get(('organization',))
            
            if pub_id:
                try:
                    pub = toolkit.get_action('organization_show')(context, {'id': pub_id})
                    pub_users = pub.get('users', [])
                    pub_display_names = [strip_unsafe(dn.get("display_name")) for dn in pub_users]
                    data[key] = pub_display_names if pub_display_names else []
                except Exception as e:
                    logging.error(f"Failed to get publisher info: {e}")
                    data[key] = []
            else:
                data[key] = []
    
    except Exception as e:
        logging.error(f"ERROR in insert_publisher: {e}")
        data[key] = []

def parse_multi_field(value):
    if value is toolkit.missing or not value:
        return []

    if isinstance(value, list):
        if len(value) == 1 and isinstance(value[0], str):
            value = value[0]
        else:
            return [strip_unsafe(item) for item in value]
    
    if not isinstance(value, str):
        return [strip_unsafe(str(value))]
    
    value = value.strip()

    if value.startswith('['):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [strip_unsafe(item) for item in parsed]
            return [strip_unsafe(parsed)]
        except (json.JSONDecodeError, ValueError):
            pass
    
    if '"' in value:
        items = re.findall(r'"([^"]*)"', value)
        if items:
            return [strip_unsafe(item) for item in items if item.strip()]
    
    if ',' in value:
        return [strip_unsafe(item) for item in value.split(',') if item.strip()]
    
    return [strip_unsafe(value)] if value else []

def json_list_normalise(value):
    if not value or (isinstance(value, list) and len(value) == 0):
        return json.dumps(['Unassigned'])
    
    if isinstance(value, list):
        return json.dumps(value)
    
    return json.dumps([str(value)])

def parse_json_list(value):
    if isinstance(value, list):
        return value  # Already a list
    
    if not isinstance(value, str):
        return [str(value)] if value else []
    
    if not value or value == 'null':
        return []
    
    attempts = [
        lambda: json.loads(value),   
        lambda: json.loads(value.replace("'", '"')),  
        lambda: json.loads(value.encode('utf-8').decode('unicode_escape')), 
    ]
    
    for attempt in attempts:
        try:
            result = attempt()
            if isinstance(result, list):
                return result
            else:
                return [result]
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
            continue
    
    return [value]
