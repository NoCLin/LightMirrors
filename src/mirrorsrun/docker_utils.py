import base64
import json
import re
import time
from typing import Dict
import httpx


class CachedToken:
    token: str
    exp: int

    def __init__(self, token, exp):
        self.token = token
        self.exp = exp


cached_tokens: Dict[str, CachedToken] = {}


# https://github.com/opencontainers/distribution-spec/blob/main/spec.md
name_regex = "[a-z0-9]+((.|_|__|-+)[a-z0-9]+)*(/[a-z0-9]+((.|_|__|-+)[a-z0-9]+)*)*"
reference_regex = "[a-zA-Z0-9_][a-zA-Z0-9._-]{0,127}"


def try_extract_image_name(path):
    pattern = r"^/v2/(.*)/([a-zA-Z]+)/(.*)$"
    match = re.search(pattern, path)

    if match:
        assert len(match.groups()) == 3
        name, resource, reference = match.groups()
        assert re.match(name_regex, name)
        assert re.match(reference_regex, reference)
        assert resource in ["manifests", "blobs", "tags"]
        return name, resource, reference

    return None, None, None


def get_docker_token(name):
    cached = cached_tokens.get(name, None)
    if cached and cached.exp > time.time():
        return cached.token

    url = "https://auth.docker.io/token"
    params = {
        "scope": f"repository:{name}:pull",
        "service": "registry.docker.io",
    }

    client = httpx.Client()
    response = client.get(url, params=params)
    response.raise_for_status()

    token_data = response.json()
    token = token_data["token"]
    payload = token.split(".")[1]
    padding = len(payload) % 4
    payload += "=" * padding

    payload = json.loads(base64.b64decode(payload))
    assert payload["iss"] == "auth.docker.io"
    assert len(payload["access"]) > 0

    cached_tokens[name] = CachedToken(exp=payload["exp"], token=token)

    return token
