# Project: a concurrent downloader

This is the module project. It puts everything together: bounded concurrency, retries with
backoff, timeouts, cancellation that cleans up, and files that are never left half-written.
Tools like `pip`, `yt-dlp` and package managers all contain a piece of code like this.

Write, in `solution.py`:

```python
def file_name(url: str) -> str

async def download_all(client, urls, dest, *, limit=4, retries=2, timeout=2.0,
                       sleep=asyncio.sleep) -> dict
```

## `file_name(url)`

The last segment of the URL's **path** (ignore `?query` and `#fragment`; `httpx.URL(url).path`
gives the path). If that segment is empty (the path ends in `/` or is empty), use
`"index.html"`.

```python
file_name("https://x.test/a/b/report.pdf")          # 'report.pdf'
file_name("https://x.test/img/cat.png?size=large")  # 'cat.png'
file_name("https://x.test/docs/")                   # 'index.html'
```

## `download_all(...)`

Download every URL with the given `httpx.AsyncClient` and save it as `dest / file_name(url)`.
You may assume the file names are all different.

1. **Destination.** `dest` is a `str` or `Path`. Create the folder (and its parents) if it does
   not exist.
2. **Concurrency.** Run the downloads concurrently, with **at most `limit`** in flight at any
   moment. `limit < 1` raises `ValueError`.
3. **Retries.** A 5xx answer or an `httpx.TransportError` (connection refused, connection lost
   in the middle of the body, ...) is retried, up to `retries` extra attempts. Before retry
   number `k + 1` wait `0.1 * 2**k` seconds (`0.1`, `0.2`, ...) by calling `await sleep(delay)`
   with the **`sleep` parameter**. A 4xx answer is not retried.
4. **Timeout.** Each attempt (request plus the whole body) must finish within `timeout`
   seconds; use `asyncio.timeout`. A timed-out download is **not** retried.
5. **Atomic files.** Write the body to `dest / (name + ".part")`, and only when the last byte is
   written rename it to the final name (`Path.replace`). A reader must never see a final file
   that is incomplete. Each attempt starts from an empty `.part` file.
6. **No leftovers.** After a failed attempt, a timeout or a cancellation, **no** `.part` file
   is left, and no final file is created for that URL.
7. **Report.** Return a dict, keys in the order of `urls`, values:
   - `"ok"`,
   - `"failed: HTTP <code>"` for a 4xx, or a 5xx after the last attempt (for example
     `"failed: HTTP 404"`),
   - `"failed: <ErrorType>"` for a transport error after the last attempt (for example
     `"failed: ConnectError"`, from `type(error).__name__`),
   - `"timeout"`.

   One failing URL never stops the others.
8. **Cancellation.** If the task running `download_all` is cancelled, every download in
   progress stops, their `.part` files are removed, files that were already completely
   downloaded stay, no task is left running, and the `CancelledError` propagates (the caller's
   `task.cancelled()` is `True`).

The tests use a fake server (`httpx.MockTransport`), never the network. Some of its answers
send the body in pieces, pause in the middle, or break the connection half-way, so you can
download with `client.stream("GET", url)` and `response.aiter_bytes()` (good for big files) or
with a plain `await client.get(url)` (the whole body in memory). Both can pass.

**Example**

```python
async with httpx.AsyncClient() as client:
    report = await download_all(client, [
        "https://example.com/files/a.zip",       # fine
        "https://example.com/files/missing.txt",  # 404
        "https://flaky.example.com/b.iso",        # 503, then fine
        "https://slow.example.com/c.tar",         # never answers
    ], "downloads", limit=2, timeout=5.0)

report
# {'https://example.com/files/a.zip': 'ok',
#  'https://example.com/files/missing.txt': 'failed: HTTP 404',
#  'https://flaky.example.com/b.iso': 'ok',
#  'https://slow.example.com/c.tar': 'timeout'}
# downloads/ contains a.zip and b.iso, and no .part files
```

Plan it before you code it: one function for **one attempt**, one for **one URL with
retries**, and `download_all` on top. Then test each rule with the test file, one at a time.
