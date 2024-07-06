from starlette.requests import Request

from mirrorsrun.proxy.direct import direct_proxy
from starlette.responses import Response


async def goproxy(request: Request):
    path = request.url.path

    sumdb_prefix = "/sumdb/sum.golang.org"
    if path.startswith(sumdb_prefix):
        sumdb_path = path.removeprefix(sumdb_prefix)
        if sumdb_path.startswith("/supported"):
            return Response(
                content=b"",
            )
        target_url = "https://sum.golang.org" + sumdb_path
        return await direct_proxy(
            request,
            target_url,
        )

    target_url = "https://proxy.golang.org" + path

    return await direct_proxy(
        request,
        target_url,
    )

