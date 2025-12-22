import base64
import hashlib
import uuid


def oauth_code_verify_and_challenge() -> tuple[str, str]:
    uuid1 = uuid.uuid4()
    uuid_str1 = str(uuid1).upper()
    code_verifier = uuid_str1 + "-" + uuid_str1
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()).decode('utf-8').replace('=', '')
    return code_verifier, code_challenge
