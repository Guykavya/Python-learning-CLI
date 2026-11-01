## Hint 1

Think of the two deadlines as two nested boxes. The small box goes around **one** request; when
it fires, only that request becomes `"timeout"`. The big box goes around **all** the requests;
when it fires, everything still running is cancelled. Where does each `asyncio.timeout(...)`
go? And if results are stored only at the very end, what happens to the ones that finished
before the big box fired?

## Hint 2

Start the dict with `"timeout"` for every url, and let each request overwrite its own entry
when it succeeds. `asyncio.TaskGroup` cancels **and waits for** its tasks when the code around
it is cancelled, which is exactly what `asyncio.timeout(total)` does when it fires.

```
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
            for url in urls: group.create_task(fetch_one(url))
except TimeoutError:
    pass
return results
```
