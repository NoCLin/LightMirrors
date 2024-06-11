import logging

from starlette.requests import Request
from starlette.responses import Response

from mirrorsrun.docker_utils import try_extract_image_name
from mirrorsrun.proxy.direct import direct_proxy
from mirrorsrun.proxy.file_cache import try_file_based_cache

logger = logging.getLogger(__name__)

BASE_URL = "https://registry.k8s.io"


async def post_process(request: Request, response: Response):
    if response.status_code == 307:
        location = response.headers["location"]

        if "/blobs/" in request.url.path:
            return await try_file_based_cache(request, location)

        return await direct_proxy(request, location)

    return response


async def k8s(request: Request):
    path = request.url.path
    if not path.startswith("/v2/"):
        return Response(content="Not Found", status_code=404)

    if path == "/v2/":
        return Response(content="OK")

    name, resource, reference = try_extract_image_name(path)

    if not name:
        return Response(content="404 Not Found", status_code=404)

    target_url = BASE_URL + f"/v2/{name}/{resource}/{reference}"

    logger.info(
        f"got docker request, {path=} {name=} {resource=} {reference=} {target_url=}"
    )

    return await direct_proxy(
        request,
        target_url,
        post_process=post_process,
    )
