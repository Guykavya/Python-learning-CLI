- Writing straight to the final file name. If the download fails or is cancelled half-way, a
  file with the right name and the wrong content is left behind, and the next run thinks it is
  done.
- Cleaning up in `except Exception:`. Timeouts and cancellation arrive as `CancelledError`, a
  `BaseException`, so the `.part` file survives exactly in the cases where cleanup matters most.
- Catching `CancelledError` (or `BaseException`) and **not** re-raising it. The download is
  reported as failed, but cancelling `download_all` no longer stops it, and `asyncio.timeout`
  can no longer turn the cancellation into `TimeoutError`.
- Opening the `.part` file with `"ab"`, or reusing it after a failed attempt. Bytes from the
  broken attempt stay at the front of the file.
- Calling `raise_for_status()` after writing the body: the 404 page is saved as `report.pdf`.
- Retrying timeouts and 4xx answers. The rules say: retry 5xx and transport errors only.
- Using `asyncio.sleep` (or `time.sleep`) for backoff instead of the `sleep` parameter. The tests
  cannot see the delays, and `time.sleep` would freeze every download.
- Creating the semaphore inside the per-URL function: every URL gets its own, so nothing is
  limited.
- `asyncio.gather(*downloads)` without cancelling on the way out. When the caller cancels,
  `gather` does cancel its children, but an exception in one of them leaves the others running;
  a TaskGroup handles both cases.
- Letting an exception from one URL escape `_download_one`. With a TaskGroup that cancels every
  other download; every expected problem must become a report entry.
- Building the report in completion order. Pre-fill it with `dict.fromkeys(urls)`.
- Taking the file name with `url.split("/")[-1]`. A query string (`cat.png?size=large`) ends up
  in the file name.
