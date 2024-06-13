from starlette.requests import Request

from mirrorsrun.proxy.direct import direct_proxy
from starlette.responses import Response


async def common(request: Request):
    path = request.url.path
    if path == "/":
        return
    if path.startswith("/alpine"):
        return await direct_proxy(request, "https://dl-cdn.alpinelinux.org" + path)
    if path.startswith("/ubuntu/"):
        return await direct_proxy(request, "http://archive.ubuntu.com" + path)
    if path.startswith("/ubuntu-ports/"):
        return await direct_proxy(request, "http://ports.ubuntu.com" + path)

    return Response("Not Found", status_code=404)
