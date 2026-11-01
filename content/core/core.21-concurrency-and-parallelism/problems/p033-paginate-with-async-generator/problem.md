# Lazy pagination with an async generator

Web APIs return long lists in **pages**: page 1 has the first 100 items, page 2 the next
100, and so on, until a page comes back empty. Callers do not want to think about pages;
they want to write

```python
async for order in paginate(fetch_page):
    ...
```

and they may stop early (`break`) after finding what they need. Pages that are never needed
must never be fetched: every request costs time and API quota.

Write `paginate(fetch_page)` in `solution.py` as an **async generator** (an `async def`
with `yield`):

- `await fetch_page(n)` returns the list of items on page `n` (pages start at 1). An empty
  list means there are no more pages.
- Yield every item of page 1, then of page 2, and so on, stopping at the first empty page.
- Fetch **lazily**: fetch page `n + 1` only when the caller asks for the item after the last
  item of page `n`. Creating the generator fetches nothing.

**Example**

```python
import asyncio

PAGES = {1: ["a", "b"], 2: ["c"], 3: ["d", "e"], 4: []}

async def fetch_page(n):
    print("fetching page", n)
    await asyncio.sleep(0.01)
    return PAGES.get(n, [])

async def main():
    async for item in paginate(fetch_page):
        print(item)
        if item == "c":
            break

asyncio.run(main())
```

Output:

```text
fetching page 1
a
b
fetching page 2
c
```

Page 3 is never fetched, because the loop stopped after `c`.
