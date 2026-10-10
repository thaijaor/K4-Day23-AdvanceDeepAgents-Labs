"""Optional Vertex OAuth authentication for the OpenAI-compatible client."""
import os
import re
import threading
from functools import lru_cache


@lru_cache(maxsize=4)
def _credential_provider(path):
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request

    credentials = service_account.Credentials.from_service_account_file(
        path, scopes=['https://www.googleapis.com/auth/cloud-platform'])
    lock = threading.Lock()

    def token():
        with lock:
            if not credentials.valid:
                credentials.refresh(Request())
            return credentials.token

    return token


def vertex_token_provider():
    path = os.getenv('LAB_VERTEX_CREDENTIALS')
    return _credential_provider(path) if path else None


def configure_vertex():
    """Configure the provided model factory without storing an access token."""
    if not os.getenv('LAB_VERTEX_CREDENTIALS'):
        return False
    project = os.getenv('LAB_VERTEX_PROJECT', '').strip()
    location = os.getenv('LAB_VERTEX_LOCATION', 'global').strip()
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,62}', project):
        raise ValueError('LAB_VERTEX_PROJECT must be a Google Cloud project ID')
    if not re.fullmatch(r'[a-z0-9-]+', location):
        raise ValueError('invalid LAB_VERTEX_LOCATION')
    host = 'aiplatform.googleapis.com' if location == 'global' else f'{location}-aiplatform.googleapis.com'
    os.environ['LAB_BASE_URL'] = f'https://{host}/v1/projects/{project}/locations/{location}/endpoints/openapi'
    # The adapter replaces this placeholder with a refreshing OAuth callback.
    os.environ['LAB_API_KEY'] = 'vertex-oauth'
    return True
