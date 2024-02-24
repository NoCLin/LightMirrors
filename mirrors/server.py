import base64
import signal
import urllib.parse

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request

from config import BASE_DOMAIN, RPC_SECRET, EXTERNAL_URL_ARIA2, EXTERNAL_HOST_ARIA2
from sites.docker import docker
from sites.npm import npm
from sites.pypi import pypi
from sites.torch import torch

app = FastAPI()


@app.middleware("http")
async def capture_request(request: Request, call_next: callable):
    hostname = request.url.hostname
    if not hostname.endswith(f".{BASE_DOMAIN}"):
        return await call_next(request)

    if hostname.startswith("pypi."):
        return await pypi(request)
    if hostname.startswith("torch."):
        return await torch(request)
    if hostname.startswith("docker."):
        return await docker(request)
    if hostname.startswith("npm."):
        return await npm(request)

    return await call_next(request)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    port = 8080
    print(f"Server started at https://*.{BASE_DOMAIN})")

    for dn in ["pypi", "torch", "docker", "npm"]:
        print(f" - https://{dn}.{BASE_DOMAIN}")

    aria2_secret = base64.b64encode(RPC_SECRET.encode()).decode()

    params = {
        'protocol': 'https',
        'host': EXTERNAL_HOST_ARIA2,
        'port': '443',
        'interface': 'jsonrpc',
        'secret': aria2_secret
    }

    query_string = urllib.parse.urlencode(params)
    aria2_url_with_auth = EXTERNAL_URL_ARIA2 + "/#!/settings/rpc/set?" + query_string

    print(f"Download manager (Aria2) at {aria2_url_with_auth}")
    uvicorn.run(app="server:app", host="0.0.0.0", port=port, reload=True, proxy_headers=True, forwarded_allow_ips="*")
