import json
import logging
import uuid

import httpx

from mirrorsrun.config import RPC_SECRET, ARIA2_RPC_URL

logger = logging.getLogger(__name__)


# refer to https://aria2.github.io/manual/en/html/aria2c.html
async def send_request(method, params=None):
    request_id = uuid.uuid4().hex
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": [f"token:{RPC_SECRET}"] + (params or []),
    }

    # specify the internal API call don't use proxy
    async with httpx.AsyncClient(
        mounts={"all://": httpx.AsyncHTTPTransport()}
    ) as client:
        response = await client.post(ARIA2_RPC_URL, json=payload)
    try:
        return response.json()
    except json.JSONDecodeError as e:
        logger.warning(
            f"aria2 request failed, response: {response.status_code} {response.text}"
        )
        raise e


async def add_download(url, save_dir="/app/cache", out_file=None):
    logger.info(f"[Aria2] add_download {url=} {save_dir=} {out_file=}")

    method = "aria2.addUri"
    options = {
        "dir": save_dir,
        "header": [],
        "out": out_file,
    }

    if out_file:
        options["out"] = out_file

    params = [[url], options]
    response = await send_request(method, params)
    return response["result"]


async def pause_download(gid):
    method = "aria2.pause"
    params = [gid]
    response = await send_request(method, params)
    return response["result"]


async def resume_download(gid):
    method = "aria2.unpause"
    params = [gid]
    response = await send_request(method, params)
    return response["result"]


async def get_status(gid):
    method = "aria2.tellStatus"
    params = [gid]
    response = await send_request(method, params)
    return response["result"]


async def list_downloads():
    method = "aria2.tellActive"
    response = await send_request(method)
    return response["result"]
