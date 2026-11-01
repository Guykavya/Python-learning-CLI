"""A concurrent downloader: limits, retries, timeouts, atomic files, clean cancellation.

Suggested shape (you may organise it differently):

    file_name(url)                      -> "report.pdf"
    _fetch_to_file(client, url, target) -> ONE attempt: stream into target.part, rename to target;
                                           on any failure or cancellation delete target.part
    _download_one(client, url, dest, retries, timeout, sleep) -> "ok" | "failed: ..." | "timeout"
    download_all(...)                   -> semaphore + one task per url + the report dict
"""

import asyncio
from pathlib import Path

import httpx

BACKOFF = 0.1          # seconds before the first retry; doubles each time


def file_name(url: str) -> str:
    """The last segment of the URL's path, or 'index.html' if it is empty."""
    raise NotImplementedError


async def download_all(client, urls, dest, *, limit=4, retries=2, timeout=2.0,
                       sleep=asyncio.sleep) -> dict:
    """Download every url into dest; return {url: "ok" | "failed: <reason>" | "timeout"}."""
    raise NotImplementedError
