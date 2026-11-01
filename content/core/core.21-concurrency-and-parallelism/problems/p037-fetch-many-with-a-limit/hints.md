## Hint 1

Two separate jobs: *start everything* (so requests can overlap) and *let only `limit` of them
past a gate* at once. Which asyncio tool runs many coroutines together and keeps their order?
Which asyncio object is a counter of free slots that makes `async with` wait when it reaches 0?

## Hint 2

```
semaphore = asyncio.Semaphore(limit)          # one, shared by all

async def status_of(url):
    async with semaphore:
        response = await client.get(url)
        return response.status_code

codes = await asyncio.gather(*[status_of(u) for u in urls])
return dict(zip(urls, codes))
```
