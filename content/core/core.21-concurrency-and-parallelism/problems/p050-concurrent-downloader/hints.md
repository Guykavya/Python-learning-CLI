## Hint 1

Split the job into three layers and give each one a single responsibility:

- **One attempt** (`_fetch_to_file`): request, check the status, write `name.part`, rename. If
  *anything* goes wrong, including a cancellation, delete `name.part` and let the exception
  continue.
- **One URL** (`_download_one`): loop over attempts, turn exceptions into a decision (return a
  report string, or sleep and retry). It never raises for HTTP or network problems.
- **All URLs** (`download_all`): folder, semaphore, one task per URL, the report dict.

Which layer owns the timeout? Which owns the semaphore? Where must cleanup happen so that it
runs for a timeout and for a cancellation too?

## Hint 2

A timeout and a cancellation both arrive inside your code as `asyncio.CancelledError`, which is
a `BaseException`, **not** an `Exception`. So `except Exception: cleanup` does not run for
them. Use `except BaseException:` (then `raise`) or `finally` for the cleanup.

```
async def _fetch_to_file(client, url, target):
    part = target.with_name(target.name + ".part")
    try:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            with open(part, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)
        part.replace(target)
    except BaseException:
        part.unlink(missing_ok=True)
        raise
```

## Hint 3

```
async def _download_one(client, url, dest, retries, timeout, sleep):
    target = dest / file_name(url)
    for attempt in range(retries + 1):
        last = attempt == retries
        try:
            async with asyncio.timeout(timeout):
                await _fetch_to_file(client, url, target)
            return "ok"
        except TimeoutError:            return "timeout"
        except HTTPStatusError as e:    if code < 500 or last: return f"failed: HTTP {code}"
        except TransportError as e:     if last: return f"failed: {type(e).__name__}"
        await sleep(0.1 * 2 ** attempt)

async def download_all(...):
    check limit; dest = Path(dest); dest.mkdir(parents=True, exist_ok=True)
    semaphore = asyncio.Semaphore(limit)
    report = dict.fromkeys(urls)
    async def worker(url):
        async with semaphore:
            report[url] = await _download_one(...)
    async with asyncio.TaskGroup() as group:
        for url in urls: group.create_task(worker(url))
    return report
```

Why does the TaskGroup give you rule 8 for free?
