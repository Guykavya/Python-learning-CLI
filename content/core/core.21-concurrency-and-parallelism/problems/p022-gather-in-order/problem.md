# Fetch everything at once with `gather`

`fetch` is an `async def` function that takes a name and returns some data after waiting on
the network (in the tests, `await asyncio.sleep(...)`).

Write `async def fetch_all(names, fetch)` in `solution.py`:

- Fetch every name **concurrently**: all waits overlap, so five 0.2-second fetches take about
  0.2 seconds, not 1 second.
- Return a list of the results **in the same order as `names`**, no matter which fetch
  finishes first.
- An empty `names` returns `[]`.

Use `asyncio.gather`.

**Example**

```python
import asyncio

async def fetch(name):
    await asyncio.sleep(0.1 * len(name))   # longer names are slower
    return name.upper()

print(asyncio.run(fetch_all(["ccc", "a", "bb"], fetch)))
# ['CCC', 'A', 'BB']    after about 0.3 s, not 0.6 s
```
