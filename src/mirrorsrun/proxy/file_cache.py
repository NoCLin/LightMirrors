import logging
import os
import pathlib
import typing
from asyncio import sleep
from enum import Enum
from urllib.parse import urlparse, quote

import httpx
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_504_GATEWAY_TIMEOUT

from mirrorsrun.aria2_api import add_download

from mirrorsrun.config import CACHE_DIR, EXTERNAL_URL_ARIA2
from typing import Optional, Callable

logger = logging.getLogger(__name__)


def get_cache_file_and_folder(url: str) -> typing.Tuple[str, str]:
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    path = parsed_url.path
    assert hostname
    assert path

    base_dir = pathlib.Path(CACHE_DIR)
    assert parsed_url.path[0] == "/"
    assert parsed_url.path[-1] != "/"
    cache_file = (base_dir / hostname / path[1:]).resolve()

    assert cache_file.is_relative_to(base_dir)

    return str(cache_file), os.path.dirname(cache_file)


class DownloadingStatus(Enum):
    DOWNLOADING = 1
    DOWNLOADED = 2
    NOT_FOUND = 3


def lookup_cache(url: str) -> DownloadingStatus:
    cache_file, _ = get_cache_file_and_folder(url)

    cache_file_aria2 = f"{cache_file}.aria2"
    if os.path.exists(cache_file_aria2):
        return DownloadingStatus.DOWNLOADING

    if os.path.exists(cache_file):
        assert not os.path.isdir(cache_file)
        return DownloadingStatus.DOWNLOADED
    return DownloadingStatus.NOT_FOUND


def make_cached_response(url):
    cache_file, _ = get_cache_file_and_folder(url)

    assert os.path.exists(cache_file)
    assert not os.path.isdir(cache_file)
    with open(cache_file, "rb") as f:
        content = f.read()
        return Response(content=content, status_code=200)


async def get_url_content_length(url):
    async with httpx.AsyncClient() as client:
        head_response = await client.head(url)
        content_len = head_response.headers.get("content-length", None)
        return content_len


async def try_file_based_cache(
    request: Request,
    target_url: str,
    download_wait_time: int = 60,
    post_process: Optional[Callable[[Request, Response], Response]] = None,
) -> Response:
    cache_status = lookup_cache(target_url)
    if cache_status == DownloadingStatus.DOWNLOADED:
        resp = make_cached_response(target_url)
        if post_process:
            resp = post_process(request, resp)
        return resp

    if cache_status == DownloadingStatus.DOWNLOADING:
        logger.info(f"Download is not finished, return 503 for {target_url}")
        return Response(
            content=f"This file is downloading, view it at {EXTERNAL_URL_ARIA2}",
            status_code=HTTP_504_GATEWAY_TIMEOUT,
        )

    assert cache_status == DownloadingStatus.NOT_FOUND

    cache_file, cache_file_dir = get_cache_file_and_folder(target_url)
    print("prepare to download", target_url, cache_file, cache_file_dir)

    processed_url = quote(target_url, safe="/:?=&%")

    try:
        await add_download(processed_url, save_dir=cache_file_dir)
    except Exception as e:
        logger.error(f"Download error, return 503500 for {target_url}", exc_info=e)
        return Response(
            content=f"Failed to add download: {e}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # wait for download finished
    for _ in range(download_wait_time):
        await sleep(1)
        cache_status = lookup_cache(target_url)
        if cache_status == DownloadingStatus.DOWNLOADED:
            return make_cached_response(target_url)
    logger.info(f"Download is not finished, return 503 for {target_url}")
    return Response(
        content=f"This file is downloading, view it at {EXTERNAL_URL_ARIA2}",
        status_code=HTTP_504_GATEWAY_TIMEOUT,
    )
