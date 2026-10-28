- Calling `islice(iterable, n)` on the original list every round. A list restarts at the
  beginning, so you get the first batch for ever.
- Forgetting the last, short batch (the plain-loop version needs the `if chunk:` at the end).
- Yielding an empty list at the end when the length is an exact multiple of `n`.
- Reusing the same list object: `chunk.clear()` after `yield chunk` empties the list the caller
  already received. Make a new list with `chunk = []`.
- Calling `list(iterable)` first and slicing. It hangs on an endless stream.
