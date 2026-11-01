## Approach

An async generator is the async twin of a normal generator: an `async def` with `yield`.
The caller drives it with `async for` (or `await anext(gen)`), and every `yield` **pauses**
the generator until the caller wants the next item. Inside it you may `await`, which is what
a normal generator cannot do and why fetching pages needs the async kind.

Laziness then comes for free if you yield items **as soon as you have them**:

1. Fetch page 1, yield its items one by one. While the caller handles them, the generator
   sits paused at `yield`; no request is made.
2. Only when the caller asks for one more item after the last item of the page does the
   generator continue, increase `page`, and fetch the next page.
3. An empty page means the end: `return` (with no value) finishes the generator, which ends
   the `async for`.

If the caller `break`s, the generator is left paused and is later closed (`aclose()`); the
next page is never fetched.

## Code

```python
async def paginate(fetch_page):
    page = 1
    while True:
        items = await fetch_page(page)
        if not items:
            return
        for item in items:
            yield item
        page += 1
```

## Complexity

O(1) extra memory: only one page is held at a time (the starter holds every item). The
number of requests is exactly the number of pages the caller actually needs, plus one empty
page if they read to the end.

## Another way

Write a class with `__aiter__` (returning `self`) and `async def __anext__`, which keeps
`page` and a buffer of the current page's items, refills the buffer with `await
fetch_page(...)` when it is empty, and raises `StopAsyncIteration` on an empty page. It is
the same machine written by hand; the generator version is shorter because Python keeps the
state (`page`, the position in `items`) for you.

`yield from` is not allowed in async generators; use the inner `for` loop.
