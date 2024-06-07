import json
import logging
import uuid

import httpx

from config import RPC_SECRET, ARIA2_RPC_URL

logger = logging.getLogger(__name__)


async def send_request(method, params=None):
    payload = {
        "jsonrpc": "2.0",
        "id": uuid.uuid4().hex,
        "method": method,
        "params": [f"token:{RPC_SECRET}"] + (params or []),
    }

    # specify the internal API call don't use proxy
    async with httpx.AsyncClient(
        mounts={"all://": httpx.AsyncHTTPTransport()}
    ) as client:
        response = await client.post(ARIA2_RPC_URL, json=payload)
    logger.info(
        f"aria2 request: {method} {params} -> {response.status_code} {response.text}"
    )
    try:
        return response.json()
    except json.JSONDecodeError as e:
        logger.warning(f"aria2 response: {response.status_code} {response.text}")
        raise e


async def add_download(url, save_dir="/app/cache"):
    method = "aria2.addUri"
    params = [[url], {"dir": save_dir, "header": []}]
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
