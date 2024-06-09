from starlette.requests import Request
from starlette.responses import Response

from mirrorsrun.proxy.file_cache import try_file_based_cache
from mirrorsrun.proxy.direct import direct_proxy

BASE_URL = "https://download.pytorch.org"


async def torch(request: Request):
    path = request.url.path

    if not path.startswith("/whl/"):
        return Response(content="Not Found", status_code=404)

    if path == "/whl":
        path = "/whl/"

    target_url = BASE_URL + path

    if path.endswith(".whl") or path.endswith(".tar.gz"):
        return await try_file_based_cache(request, target_url)

    return await direct_proxy(
        request,
        target_url,
    )
