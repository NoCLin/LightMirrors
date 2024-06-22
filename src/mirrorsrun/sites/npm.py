from starlette.requests import Request

from mirrorsrun.config import BASE_URL_NPM
from mirrorsrun.proxy.direct import direct_proxy


async def npm(request: Request):
    path = request.url.path

    return await direct_proxy(request, BASE_URL_NPM + path)
