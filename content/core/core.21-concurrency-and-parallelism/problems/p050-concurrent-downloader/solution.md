## Approach

### Three layers

| Layer | Knows about | Decides |
|---|---|---|
| `_fetch_to_file` | one HTTP attempt, one `.part` file | nothing: success, or clean up and re-raise |
| `_download_one` | attempts, backoff, the timeout | the report string for one URL |
| `download_all` | the folder, the limit, all URLs | nothing new: runs the others, collects the report |

Keeping decisions out of the bottom layer is what makes the rules easy to check: cleanup is in
exactly one place, retry policy is in exactly one place.

### One attempt: atomic writes

The body goes to `name.part`, opened with `"wb"` (truncate: a retry starts empty). Only after
the last chunk is written is it renamed with `Path.replace`, which on the same file system is
**atomic**: the final name goes from "does not exist" to "complete file" in one step. Anyone
looking at the folder (a user, another program, the next run of this downloader) sees either
nothing or the full file, never half of it.

The `except BaseException: part.unlink(missing_ok=True); raise` block is the heart of the
cleanup rules. It runs for an HTTP error, a broken connection, a timeout and a cancellation.
The last two are delivered as `asyncio.CancelledError` at whatever `await` the code is at, and
`CancelledError` is a `BaseException`, so `except Exception` would miss them. The bare `raise`
re-raises the same exception: cleanup must never swallow it. `missing_ok=True` covers the case
where the error came before the file was opened (a 404, a refused connection).

`raise_for_status()` is called **before** opening the file, so an error page is never saved as
`report.pdf`.

### One URL: retries and the timeout

`asyncio.timeout(timeout)` wraps one whole attempt (request and body). When it fires, it
cancels the attempt (which cleans up its `.part`) and then raises `TimeoutError`, which we
turn into `"timeout"`. The retry decision is the same table as p038, but the result is a report
string instead of an exception, so one bad URL cannot break the batch. Note that the `sleep`
for backoff is outside the timeout: waiting between attempts does not use up an attempt's time.

What if `download_all` itself is cancelled while `_download_one` is inside an attempt or a
backoff `sleep`? The `CancelledError` passes straight through: `except TimeoutError`,
`except httpx.HTTPStatusError` and `except httpx.TransportError` do not match it, and the
`asyncio.timeout` context lets a cancellation it did not cause pass unchanged.

### All URLs: the limit and cancellation

`asyncio.Semaphore(limit)` around each download keeps at most `limit` in flight. The report
is pre-filled with `dict.fromkeys(urls)`, so its keys are in input order whatever order the
downloads finish in.

The `TaskGroup` provides rule 8. When the task running `download_all` is cancelled, the
cancellation lands at the end of the `async with TaskGroup()` block, where it is waiting. The
group then cancels every child task (each one cleans up its `.part` through the `except
BaseException` above), **waits** for all of them, and re-raises the `CancelledError` to the
caller. Downloads that had finished keep their files, because their rename already happened.

## Code

```python
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
```

## Complexity

n URLs, at most `limit` downloads at a time; each URL makes at most `retries + 1` requests. With
streaming, memory per download is one chunk (a few KB), so the total is O(limit) chunks however
big the files are; `await client.get` instead holds each whole body in memory. Wall time is
roughly `ceil(n / limit)` download times, plus backoff waits for flaky URLs.

## Another way

- **Free the slot during backoff.** Here a URL keeps its semaphore slot while it sleeps before a
  retry. Taking the semaphore inside `_download_one` around each attempt only (not around the
  sleep) lets other URLs use the slot meanwhile. Both obey "at most `limit` in flight".
- **A worker pool.** Instead of one task per URL behind a semaphore, start `limit` workers that
  pull URLs from an `asyncio.Queue`. For millions of URLs that avoids creating millions of tasks
  at once.
- **Resume instead of restart.** Real downloaders keep the `.part` file after a broken
  connection and ask the server for the rest with a `Range: bytes=<size>-` header (if the server
  answers 206). That is a nice extension once the basic rules work.
- **Writing without blocking.** `f.write` on a local disk is fast enough here, but it is a
  blocking call; for very fast networks and slow disks, `asyncio.to_thread(f.write, chunk)` keeps
  the loop free.
- **Duplicate names.** Two URLs ending in `/data.csv` would overwrite each other. A real tool
  adds a suffix (`data (1).csv`) or keeps the host in the path.
