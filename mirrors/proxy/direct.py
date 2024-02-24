import typing

import httpx
import starlette.requests
import starlette.responses

from config import PROXY


async def direct_proxy(
        request: starlette.requests.Request,
        target_url: str,
        pre_process: typing.Callable[[starlette.requests.Request, httpx.Request], httpx.Request] = None,
        post_process: typing.Callable[[starlette.requests.Request, httpx.Response], httpx.Response] = None,
) -> typing.Optional[starlette.responses.Response]:
    async with httpx.AsyncClient(proxy=PROXY, verify=False) as client:

        headers = request.headers.mutablecopy()
        for key in headers.keys():
            if key not in ["user-agent", "accept"]:
                del headers[key]

        httpx_req = client.build_request(request.method, target_url, headers=headers, )

        if pre_process:
            httpx_req = pre_process(request, httpx_req)
        upstream_response = await client.send(httpx_req)

        # TODO: move to post_process
        if upstream_response.status_code == 307:
            location = upstream_response.headers["location"]
            print("catch redirect", location)

        headers = upstream_response.headers
        cl = headers.pop("content-length", None)
        ce = headers.pop("content-encoding", None)
        # print(target_url, cl, ce)
        content = upstream_response.content
        response = starlette.responses.Response(
            headers=headers,
            content=content,
            status_code=upstream_response.status_code)

        if post_process:
            response = post_process(request, response)

        return response
