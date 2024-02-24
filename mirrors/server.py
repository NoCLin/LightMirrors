import base64
import signal
import urllib.parse

import httpx
import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.staticfiles import StaticFiles

from config import BASE_DOMAIN, RPC_SECRET, EXTERNAL_URL_ARIA2, EXTERNAL_HOST_ARIA2, SCHEME
from sites.docker import docker
from sites.npm import npm
from sites.pypi import pypi
from sites.torch import torch

app = FastAPI()

app.mount("/aria2/", StaticFiles(directory="/wwwroot/"), name="static", )


async def aria2(request: Request, call_next):
    if request.url.path == "/":
        return RedirectResponse("/aria2/index.html")
    if request.url.path == "/jsonrpc":
        async with httpx.AsyncClient(mounts={
            "all://": httpx.AsyncHTTPTransport()
        }) as client:
            data = (await request.body())
            response = await client.request(url="http://aria2:6800/jsonrpc",
                                            method=request.method,
                                            headers=request.headers, content=data)
            headers = response.headers
            headers.pop("content-length", None)
            headers.pop("content-encoding", None)
            return Response(content=response.content, status_code=response.status_code, headers=headers)
    return await call_next(request)


@app.middleware("http")
async def capture_request(request: Request, call_next: callable):
    hostname = request.url.hostname
    if not hostname.endswith(f".{BASE_DOMAIN}"):
        return await call_next(request)

    if hostname.startswith("aria2."):
        return await aria2(request, call_next)

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
    port = 80
    print(f"Server started at {SCHEME}://*.{BASE_DOMAIN})")

    for dn in ["pypi", "torch", "docker", "npm"]:
        print(f" - {SCHEME}://{dn}.{BASE_DOMAIN}")

    aria2_secret = base64.b64encode(RPC_SECRET.encode()).decode()

    params = {
        'protocol': SCHEME,
        'host': EXTERNAL_HOST_ARIA2,
        'port': '443' if SCHEME == 'https' else '80',
        'interface': 'jsonrpc',
        'secret': aria2_secret
    }

    query_string = urllib.parse.urlencode(params)
    aria2_url_with_auth = EXTERNAL_URL_ARIA2 + "#!/settings/rpc/set?" + query_string

    print(f"Download manager (Aria2) at {aria2_url_with_auth}")
    # FIXME: only proxy headers if SCHME is https
    # reload only in dev mode
    uvicorn.run(app="server:app", host="0.0.0.0", port=port, reload=True, proxy_headers=True, forwarded_allow_ips="*")
