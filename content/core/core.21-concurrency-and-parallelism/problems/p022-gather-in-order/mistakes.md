- `for name in names: results.append(await fetch(name))`. Correct results, zero
  concurrency: the total time is the sum of all fetches.
- `[await fetch(n) for n in names]`. The same thing written as a comprehension: still one
  by one.
- `asyncio.gather([fetch(n) for n in names])` (a list, no `*`). `gather` wants separate
  arguments; a list is not awaitable and raises `TypeError`.
- Sorting the results by finishing time or using `as_completed`. `gather` keeps input order
  for you; `as_completed` would lose it.
- Forgetting `await` before `asyncio.gather(...)`. You return a future instead of a list.
