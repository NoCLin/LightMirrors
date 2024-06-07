import re

from starlette.requests import Request
from starlette.responses import Response

from proxy.direct import direct_proxy
from proxy.file_cache import try_file_based_cache

pypi_file_base_url = "https://files.pythonhosted.org"
pypi_base_url = "https://pypi.org"


def pypi_replace(request: Request, response: Response) -> Response:
    is_detail_page = re.search(r"/simple/([^/]+)/", request.url.path) is not None
    if not is_detail_page:
        return response

    if is_detail_page:
        mirror_url = f"{request.url.scheme}://{request.url.netloc}"
        content = response.body
        content = content.replace(pypi_file_base_url.encode(), mirror_url.encode())
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
        target_url = pypi_base_url + path
    elif path.startswith("/packages/"):
        target_url = pypi_file_base_url + path
    else:
        return Response(content="Not Found", status_code=404)

    if path.endswith(".whl") or path.endswith(".tar.gz"):
        return await try_file_based_cache(request, target_url)

    return await direct_proxy(request, target_url, post_process=pypi_replace)
