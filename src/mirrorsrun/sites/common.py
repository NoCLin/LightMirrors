from starlette.requests import Request

from mirrorsrun.config import BASE_URL_ALPINE, BASE_URL_UBUNTU, BASE_URL_UBUNTU_PORTS
from mirrorsrun.proxy.direct import direct_proxy
from starlette.responses import Response


async def common(request: Request):
    path = request.url.path
    if path == "/":
        return
    if path.startswith("/alpine"):
        return await direct_proxy(request, BASE_URL_ALPINE + path)
    if path.startswith("/ubuntu/"):
        return await direct_proxy(request, BASE_URL_UBUNTU + path)
    if path.startswith("/ubuntu-ports/"):
        return await direct_proxy(request, BASE_URL_UBUNTU_PORTS + path)

    return Response("Not Found", status_code=404)
