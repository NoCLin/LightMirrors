import base64
import json
import re
import time
from typing import Dict

import httpx
from starlette.requests import Request
from starlette.responses import Response

from proxy.file_cache import try_file_based_cache
from proxy.direct import direct_proxy

BASE_URL = "https://registry-1.docker.io"

cached_token: Dict[str, str] = {

}

# https://github.com/opencontainers/distribution-spec/blob/main/spec.md
name_regex = "[a-z0-9]+((\.|_|__|-+)[a-z0-9]+)*(\/[a-z0-9]+((\.|_|__|-+)[a-z0-9]+)*)*"
reference_regex = "[a-zA-Z0-9_][a-zA-Z0-9._-]{0,127}"


def try_extract_image_name(path):
    pattern = rf"^/v2/(.*)/([a-zA-Z]+)/(.*)$"
    match = re.search(pattern, path)

    if match:
        assert len(match.groups()) == 3
        name, operation, reference = match.groups()
        assert re.match(name_regex, name)
        assert re.match(reference_regex, reference)
        assert operation in ["manifests", "blobs"]
        return name, operation, reference

    return None, None, None


def get_docker_token(name):
    cached = cached_token.get(name, {})
    exp = cached.get("exp", 0)

    if exp > time.time():
        return cached.get("token", 0)

    url = "https://auth.docker.io/token"
    params = {
        "scope": f"repository:{name}:pull",
        "service": "registry.docker.io",
    }

    response = httpx.get(url, params=params, verify=False)
    response.raise_for_status()

    token_data = response.json()
    token = token_data["token"]
    payload = (token.split(".")[1])
    padding = len(payload) % 4
    payload += "=" * padding

    payload = json.loads(base64.b64decode(payload))
    assert payload["iss"] == "auth.docker.io"
    assert len(payload["access"]) > 0

    cached_token[name] = {
        "exp": payload["exp"],
        "token": token
    }

    return token


def inject_token(name: str, req: Request, httpx_req: httpx.Request):
    docker_token = get_docker_token(f"{name}")
    httpx_req.headers["Authorization"] = f"Bearer {docker_token}"
    return httpx_req


async def post_process(request: Request, response: Response):
    if response.status_code == 307:
        location = response.headers["location"]
        # TODO: logger
        print("[redirect]", location)
        return await try_file_based_cache(request, location)

    return response


async def docker(request: Request):
    path = request.url.path
    print("[request]", request.method, request.url)
    if not path.startswith("/v2/"):
        return Response(content="Not Found", status_code=404)

    if path == "/v2/":
        return Response(content="OK")
        # return await direct_proxy(request, BASE_URL + '/v2/')

    name, operation, reference = try_extract_image_name(path)

    if not name:
        return Response(content='404 Not Found', status_code=404)

    # support docker pull xxx which name without library
    if '/' not in name:
        name = f"library/{name}"

    target_url = BASE_URL + f"/v2/{name}/{operation}/{reference}"

    # logger
    print('[PARSED]', path, name, operation, reference, target_url)

    return await direct_proxy(request, target_url,
                              pre_process=lambda req, http_req: inject_token(name, req, http_req),
                              post_process=post_process)
