import time

import ckan.plugins.toolkit as toolkit
from flask import flash, request, session

from . import databricksbp
from .utils import oauth_code_verify_and_challenge
from .workspace import DatabricksWorkspace


@databricksbp.route('/databricks/auth/initiate/<resource_id>')
def authenticate(resource_id):
    referrer = request.args.get("referrer", "/dataset")
    code_verifier, code_challenge = oauth_code_verify_and_challenge()

    session['databricks'] = {
        "code_verifier": code_verifier,
        "referrer": referrer
    }

    auth_url = DatabricksWorkspace.build_databricks_auth_url(code_challenge, resource_id)
    return toolkit.redirect_to(auth_url)


@databricksbp.route('/databricks/auth')
def authorise():
    workspace = DatabricksWorkspace()
    try:
        referrer = session.get('databricks', {}).get('referrer', '/')
        auth_code = workspace.get_workspace_auth_code()
        code_verifier = session.get('databricks', {}).get('code_verifier')
        response_dict = workspace.generate_workspace_access_token(code_verifier, auth_code)

        access_token = response_dict.get("access_token")
        refresh_token = response_dict.get("refresh_token")
        now = time.time()
        expires_at = int(now) + int(response_dict.get("expires_in", 3600))
        refresh_expires_at = int(now) + 604800 # 7 days

        workspace.set_tokens(access_token, refresh_token, expires_at, refresh_expires_at)
        session.pop('databricks', None)

        return toolkit.redirect_to(referrer)

    except Exception as e:
        flash(f"Download authorisation failed: {e}.", category='alert-danger')
        return toolkit.redirect_to(referrer)
