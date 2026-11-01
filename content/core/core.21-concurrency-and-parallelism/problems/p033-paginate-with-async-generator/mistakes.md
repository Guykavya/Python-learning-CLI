- Collecting every page into a list and then yielding (the starter). The caller sees the
  first item only after **all** pages are fetched, and stopping early saves nothing.
- `return all_items` from an `async def` without `yield`. That is a coroutine returning a
  list; `async for` over it fails with `TypeError`.
- Using a plain `def` generator and calling `fetch_page(n)` without `await`. You yield
  coroutine objects, not items.
- Stopping when a page is shorter than the first one. APIs often return uneven pages; only an
  empty page means the end.
- Starting at page 0, or fetching the next page before yielding the current one ("prefetch").
  Prefetching can be a deliberate speed trick, but it breaks the "fetch only what is needed"
  rule of this task.
