## Approach

Three ideas fit together:

1. **Default first.** `results` starts as `{url: "timeout"}` for every url, in input order.
   A request that succeeds overwrites its own entry as soon as it finishes. So whatever moment
   the big deadline fires, `results` already holds everything that finished, and the rest is
   correctly `"timeout"`.
2. **Inner deadline.** `async with asyncio.timeout(per_request)` around one `client.get`. When
   it fires, the request is cancelled, the context manager turns the cancellation into
   `TimeoutError`, and `fetch_one` catches it and returns. Only that url is affected.
3. **Outer deadline.** `asyncio.timeout(total)` around a `TaskGroup` holding all the tasks.
   When it fires it cancels the *current* task, which is waiting at the end of the
   `async with TaskGroup()` block. The TaskGroup reacts by cancelling every child **and
   waiting until each has finished cancelling**, then lets the cancellation out, and
   `asyncio.timeout` turns it into `TimeoutError`, which we catch.

Why does the inner `except TimeoutError` not swallow the outer deadline? When the *outer*
deadline cancels a request, the inner `asyncio.timeout` sees a cancellation it did not cause,
so it lets the `CancelledError` pass through unchanged. `except TimeoutError` does not catch
`CancelledError`, and the task ends as cancelled, as it should.

Point 3 is what the "nothing left running" tests check. `asyncio.wait(tasks, timeout=total)`
only *stops waiting*; the tasks keep running in the background, still using the connection and
writing into `results` after you returned it.

## Code

```python
import asyncio

import httpx


async def fetch_with_deadlines(client, urls, per_request, total):
    results = {url: "timeout" for url in urls}

    async def fetch_one(url):
        try:
            async with asyncio.timeout(per_request):
                response = await client.get(url)
        except TimeoutError:
            return
        results[url] = response.text

    try:
        async with asyncio.timeout(total):
            async with asyncio.TaskGroup() as group:
                for url in urls:
                    group.create_task(fetch_one(url))
    except TimeoutError:
        pass
    return results
```

## Complexity

n tasks, all overlapping. Wall time is at most about `min(total, per_request, slowest request)`
plus the time to cancel. Memory O(n).

## Another way

With `asyncio.wait`:

```python
tasks = {asyncio.create_task(fetch_one(url)) for url in urls}
if tasks:                                        # asyncio.wait refuses an empty set
    done, pending = await asyncio.wait(tasks, timeout=total)
    for task in pending:
        task.cancel()
    await asyncio.gather(*pending, return_exceptions=True)   # wait for the cancels to finish
```

This makes every step visible (stop waiting, cancel, wait for the cancels), which is good for
learning. The TaskGroup version does the same three steps for you and also cannot forget the
last one. Note that an unexpected error in one request (a bug) makes a TaskGroup cancel the
siblings and raise an `ExceptionGroup`; with `asyncio.wait` you would have to look at each
done task yourself.
