import typing
from typing import Callable, Coroutine

import httpx
from httpx import Request as HttpxRequest
from starlette.requests import Request
from starlette.responses import Response

SyncPreProcessor = Callable[[Request, HttpxRequest], HttpxRequest]

AsyncPreProcessor = Callable[
    [Request, HttpxRequest],
    Coroutine[Request, HttpxRequest, HttpxRequest]
]

SyncPostProcessor = Callable[[Request, Response], Response]

AsyncPostProcessor = Callable[
    [Request, Response],
    Coroutine[Request, Response, Response]
]


async def direct_proxy(
        request: Request,
        target_url: str,
        pre_process: typing.Union[SyncPreProcessor, AsyncPreProcessor, None] = None,
        post_process: typing.Union[SyncPostProcessor, AsyncPostProcessor, None] = None,
        cache_ttl: int = 3600,
) -> Response:
    # httpx will use the following environment variables to determine the proxy
    # https://www.python-httpx.org/environment_variables/#http_proxy-https_proxy-all_proxy
    async with httpx.AsyncClient() as client:
        req_headers = request.headers.mutablecopy()
        for key in req_headers.keys():
            if key not in ["user-agent", "accept"]:
                del req_headers[key]

        httpx_req: HttpxRequest = client.build_request(request.method, target_url, headers=req_headers, )

        if pre_process:
            new_httpx_req = pre_process(request, httpx_req)
            if isinstance(new_httpx_req, HttpxRequest):
                httpx_req = new_httpx_req
            else:
                httpx_req = await new_httpx_req

        upstream_response = await client.send(httpx_req)

        res_headers = upstream_response.headers

        cl = res_headers.pop("content-length", None)
        ce = res_headers.pop("content-encoding", None)
        # print(target_url, cl, ce)
        content = upstream_response.content
        response = Response(
            headers=res_headers,
            content=content,
            status_code=upstream_response.status_code
        )

        if post_process:
            new_res = post_process(request, response)
            if isinstance(new_res, Response):
                final_res = new_res
            elif isinstance(new_res, Coroutine):
                final_res = await new_res
        else:
            final_res = response

        return final_res
