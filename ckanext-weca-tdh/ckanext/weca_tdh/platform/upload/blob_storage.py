import json
from typing import Any

import ckanext.weca_tdh.config as C
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


class BlobStorage:
    """Manage Azure Blob Storage client"""

    @staticmethod
    def get_blob_service_client():
        account_url = f"https://{C.TDH_UPLOAD_STORAGE_ACCOUNT}.blob.core.windows.net"
        default_credential = DefaultAzureCredential()
        return BlobServiceClient(account_url, credential=default_credential)

    def upload_blob(self, file, blob_name) -> None:
        blob_client = self.get_blob_service_client().get_blob_client(
            container=C.TDH_UPLOAD_STORAGE_CONTAINER, blob=blob_name
        )
        blob_client.upload_blob(file)

    def download_blob_as_json(self, blob_name: str) -> Any:
        blob_client = self.get_blob_service_client().get_blob_client(
            container=C.TDH_UPLOAD_STORAGE_CONTAINER, blob=blob_name
        )
        return json.loads(blob_client.download_blob().content_as_text())
    