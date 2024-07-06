import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # noqa: E402

import base64
import signal
import urllib.parse
from typing import Callable
import logging

import httpx
import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.staticfiles import StaticFiles

from mirrorsrun.config import (
    BASE_DOMAIN,
    RPC_SECRET,
    EXTERNAL_URL_ARIA2,
    EXTERNAL_HOST_ARIA2,
    SCHEME, SSL_SELF_SIGNED,
)

from mirrorsrun.sites.npm import npm
from mirrorsrun.sites.pypi import pypi
from mirrorsrun.sites.torch import torch
from mirrorsrun.sites.docker import dockerhub, k8s, quay, ghcr, nvcr
from mirrorsrun.sites.common import common
from mirrorsrun.sites.goproxy import goproxy

subdomain_mapping = {
    "mirrors": common,
    "pypi": pypi,
    "torch": torch,
    "npm": npm,
    "docker": dockerhub,
    "k8s": k8s,
    "ghcr": ghcr,
    "quay": quay,
    "nvcr": nvcr,
    "goproxy": goproxy,
}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.mount(
    "/aria2/",
    StaticFiles(directory="/wwwroot/"),
    name="static",
)


async def aria2(request: Request, call_next):
    if request.url.path == "/":
        return RedirectResponse("/aria2/index.html")
    if request.url.path == "/jsonrpc":
        # dont use proxy for internal API
        async with httpx.AsyncClient(
            mounts={"all://": httpx.AsyncHTTPTransport()}
        ) as client:
            data = await request.body()
            response = await client.request(
                url="http://aria2:6800/jsonrpc",
                method=request.method,
                headers=request.headers,
                content=data,
            )
            headers = response.headers
            headers.pop("content-length", None)
            headers.pop("content-encoding", None)
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=headers,
            )
    return await call_next(request)


@app.middleware("http")
async def capture_request(request: Request, call_next: Callable):
    hostname = request.url.hostname
    if not hostname:
        return Response(content="Bad Request", status_code=400)

    if not hostname.endswith(f".{BASE_DOMAIN}"):
        return await call_next(request)

    if hostname.startswith("aria2."):
        return await aria2(request, call_next)

    subdomain = hostname.split(".")[0]

    if subdomain in subdomain_mapping:
        return await subdomain_mapping[subdomain](request)

    return await call_next(request)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    port = 80
    logger.info(f"Server started at {SCHEME}://*.{BASE_DOMAIN})")

    for dn in subdomain_mapping.keys():
        logger.info(f" - {SCHEME}://{dn}.{BASE_DOMAIN}")

    aria2_secret = base64.b64encode(RPC_SECRET.encode()).decode()

    params = {
        "protocol": SCHEME,
        "host": EXTERNAL_HOST_ARIA2,
        "port": "443" if SCHEME == "https" else "80",
        "interface": "jsonrpc",
        "secret": aria2_secret,
    }

    query_string = urllib.parse.urlencode(params)
    aria2_url_with_auth = EXTERNAL_URL_ARIA2 + "#!/settings/rpc/set?" + query_string

    logger.info(f"Download manager (Aria2) at {aria2_url_with_auth}")

    uvicorn.run(
        app="server:app",
        host="0.0.0.0",
        ssl_keyfile='/app/certs/private.key' if SSL_SELF_SIGNED else None,
        ssl_certfile='/app/certs/certificate.pem' if SSL_SELF_SIGNED else None,
        port=443 if SSL_SELF_SIGNED else 80,
        reload=True,  # TODO: reload only in dev mode
        proxy_headers=not SSL_SELF_SIGNED,  # trust x-forwarded-for etc.
        forwarded_allow_ips="*",
    )
