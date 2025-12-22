import ckanext.weca_tdh.config as C
import requests


def call_http_trigger(body: dict):
    url = C.TDH_UPLOAD_HTTP_TRIGGER
    response = requests.post(url, json=body)

    if not response.ok:
        raise Exception(f"HTTP trigger failed with status code {response.status_code}")
