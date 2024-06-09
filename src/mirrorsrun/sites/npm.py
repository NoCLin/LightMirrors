from starlette.requests import Request

from mirrorsrun.proxy.direct import direct_proxy

BASE_URL = "https://registry.npmjs.org/"


async def npm(request: Request):
    path = request.url.path

    return await direct_proxy(request, BASE_URL + path)
