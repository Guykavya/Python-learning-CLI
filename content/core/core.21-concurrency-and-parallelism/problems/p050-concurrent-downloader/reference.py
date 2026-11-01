"""A concurrent downloader: limits, retries, timeouts, atomic files, clean cancellation."""

import asyncio
from pathlib import Path

import httpx

BACKOFF = 0.1          # seconds before the first retry; doubles each time


def file_name(url: str) -> str:
    """The last segment of the URL's path, or 'index.html' if it is empty."""
    name = httpx.URL(url).path.rsplit("/", 1)[-1]
    return name or "index.html"


async def _fetch_to_file(client: httpx.AsyncClient, url: str, target: Path) -> None:
    """One attempt: stream the body into target.part, then rename it to target.

    On ANY way out other than success (HTTP error, network error, timeout, cancellation)
    the .part file is removed and the exception goes on.
    """
    part = target.with_name(target.name + ".part")
    try:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            with open(part, "wb") as f:                # "wb": a retry starts from empty
                async for chunk in response.aiter_bytes():
                    f.write(chunk)
        part.replace(target)                           # atomic: the full file appears at once
    except BaseException:                              # includes CancelledError
        part.unlink(missing_ok=True)
        raise


async def _download_one(client, url, dest, retries, timeout, sleep) -> str:
    """Download one url with retries; return its report string."""
    target = dest / file_name(url)
    for attempt in range(retries + 1):
        last = attempt == retries
        try:
            async with asyncio.timeout(timeout):
                await _fetch_to_file(client, url, target)
            return "ok"
        except TimeoutError:
            return "timeout"                           # a hung server is not retried
        except httpx.HTTPStatusError as error:
            code = error.response.status_code
            if code < 500 or last:
                return f"failed: HTTP {code}"
        except httpx.TransportError as error:
            if last:
                return f"failed: {type(error).__name__}"
        await sleep(BACKOFF * 2**attempt)
    raise AssertionError("unreachable")


async def download_all(client, urls, dest, *, limit=4, retries=2, timeout=2.0,
                       sleep=asyncio.sleep) -> dict:
    """Download every url into dest; return {url: "ok" | "failed: <reason>" | "timeout"}."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    semaphore = asyncio.Semaphore(limit)
    report = dict.fromkeys(urls)                       # keeps the input order

    async def worker(url):
        async with semaphore:
            report[url] = await _download_one(client, url, dest, retries, timeout, sleep)

    async with asyncio.TaskGroup() as group:           # cancelling us cancels every worker
        for url in urls:
            group.create_task(worker(url))
    return report
