from datetime import datetime

def filter_datetime(string, format='full'):   
    try:
        dt = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%f')   
    except:
        ValueError, TypeError
        return ""
    if format == 'short':
        return dt.strftime('%d %b %Y')        
    return dt.strftime('%d %b %Y %H:%M:%S')
