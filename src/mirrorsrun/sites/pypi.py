import re

from starlette.requests import Request
from starlette.responses import Response

from mirrorsrun.config import BASE_URL_PYPI, BASE_URL_PYPI_FILES
from mirrorsrun.proxy.direct import direct_proxy
from mirrorsrun.proxy.file_cache import try_file_based_cache


def pypi_replace(request: Request, response: Response) -> Response:
    is_detail_page = re.search(r"/simple/([^/]+)/", request.url.path) is not None
    if not is_detail_page:
        return response

    if is_detail_page:
        mirror_url = f"{request.url.scheme}://{request.url.netloc}"
        content = response.body
        content = content.replace(BASE_URL_PYPI_FILES.encode(), mirror_url.encode())
        response.body = content
        del response.headers["content-length"]
        del response.headers["content-encoding"]
        return response


async def pypi(request: Request) -> Response:
    # TODO: a debug flag to show origin url
    path = request.url.path
    if path == "/simple":
        path = "/simple/"

    if path.startswith("/simple/"):
        # FIXME: join
        target_url = BASE_URL_PYPI + path
    elif path.startswith("/packages/"):
        target_url = BASE_URL_PYPI_FILES + path
    else:
        return Response(content="Not Found", status_code=404)

    if path.endswith(".whl") or path.endswith(".tar.gz"):
        return await try_file_based_cache(request, target_url)

    return await direct_proxy(request, target_url, post_process=pypi_replace)
