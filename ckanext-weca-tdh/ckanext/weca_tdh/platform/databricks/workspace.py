import logging
import time

import ckan.plugins.toolkit as toolkit
import ckanext.weca_tdh.config as C
import requests
from ckanext.weca_tdh.platform.redis_config import RedisConfig
from ckanext.weca_tdh.platform.upload.blob_storage import BlobStorage
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import Disposition, Format, StatementState
from flask import request

log = logging.getLogger(__name__)
redis_client = RedisConfig(C.REDIS_URL)


class DatabricksWorkspace(object):
    def __init__(self):
        self.host = C.TDH_CONNECT_ADDRESS_HOST
        self.warehouse_id = str(C.TDH_CONNECT_ADDRESS_PATH).split('/')[-1]
        
    @property
    def user_id(self):
        return toolkit.current_user.id if toolkit.current_user else "anon"
    
    def get_workspace_client(self):
        return WorkspaceClient(host=self.host, token=self.get_workspace_access_token())
    
    def execute_statement(self, client, statement, timeout=30):
        stmt = client.statement_execution.execute_statement(
            statement=statement,
            warehouse_id=self.warehouse_id,
            disposition=Disposition.EXTERNAL_LINKS,
            format=Format.CSV
        )
        
        start_time = time.time()
        status = stmt.status.state

        while status in (StatementState.PENDING, StatementState.RUNNING):
            if time.time() - start_time > timeout:
                raise TimeoutError("SQL execution timed out")
            time.sleep(1)
            stmt = client.statement_execution.get_statement(stmt.statement_id)
            status = stmt.status.state

        if status != StatementState.SUCCEEDED:
            raise Exception(f"SQL execution failed: {stmt.status}")

        return stmt
    
    def set_tokens(self, access_token, refresh_token, expires_at, refresh_expires_at):
        redis_client.set_databricks_tokens(self.user_id, access_token, refresh_token, expires_at, refresh_expires_at)

    def get_tokens(self):
        return redis_client.get_databricks_tokens(self.user_id)

    def delete_tokens(self):
        redis_client.delete_databricks_tokens(self.user_id)
    
    @staticmethod
    def build_databricks_auth_url(code_challenge: str, resource_id: str) -> str:
        client_id = C.TDH_DB_APP_CLIENT_ID
        redirect_url = C.TDH_DB_APP_REDIRECT_URL

        return (
            f"https://{C.TDH_CONNECT_ADDRESS_HOST}/oidc/v1/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_url}"
            f"&response_type=code"
            f"&state={resource_id}"
            f"&code_challenge={code_challenge}"
            f"&code_challenge_method=S256"
            f"&scope=all-apis+offline_access"
        )
        
    @staticmethod
    def get_workspace_auth_code() -> str:  
        return request.args.get('code')

    def generate_workspace_access_token(self, code_verifier: str, auth_code: str) -> dict:
        base_url = f"https://{self.host}/oidc/v1/token"
        client_id = C.TDH_DB_APP_CLIENT_ID
        redirect_url = C.TDH_DB_APP_REDIRECT_URL

        data = {
            "client_id": client_id,
            "grant_type": "authorization_code",
            "scope": "all-apis offline_access",
            "redirect_uri": redirect_url,
            "code_verifier": code_verifier,
            "code": auth_code
        }

        try:
            response = requests.post(base_url, data=data)
            response_dict = response.json()
            return response_dict
        except Exception:
            raise Exception('invalid access token')
        
    def get_workspace_access_token(self) -> str:
        token_data = self.get_tokens()

        if not token_data:
            raise Exception("Databricks session expired. Please log in again")

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_at = int(token_data.get("expires_at", 0))
        refresh_expires_at = int(token_data.get("refresh_expires_at", 0))
        
        now = time.time()

        # Refresh access token if expired
        if now > expires_at:
            if not refresh_token or now > refresh_expires_at:
                self.delete_tokens()
                raise Exception("Databricks session expired. Please log in again")

            access_token = self.refresh_workspace_access_token(refresh_token, refresh_expires_at)

        return access_token

    def refresh_workspace_access_token(self, refresh_token: str, refresh_expires_at: int) -> str:
        base_url = f"https://{self.host}/oidc/v1/token"
        client_id = C.TDH_DB_APP_CLIENT_ID

        data = {
            "client_id": client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        response = requests.post(base_url, data=data)
        response_dict = response.json()

        if "access_token" not in response_dict:
            self.delete_tokens()
            raise Exception("Failed to refresh Databricks session. Please log in again")

        access_token = response_dict["access_token"]
        expires_at = int(time.time()) + int(response_dict.get("expires_in", 3600))
        
        self.set_tokens(access_token, refresh_token, expires_at, refresh_expires_at)

        return access_token

    @staticmethod
    def get_catalog_files(resource_id):
        json_data = BlobStorage().download_blob_as_json('databricks.json')
        catalog_files = json_data.get("catalog_files", {})
        return catalog_files.get(resource_id, None)
    