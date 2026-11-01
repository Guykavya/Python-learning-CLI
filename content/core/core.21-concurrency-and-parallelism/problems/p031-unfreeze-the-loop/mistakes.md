- Making the function `async def` and calling `slow_lookup` directly. `async` does not make
  a blocking call non-blocking.
- `await asyncio.to_thread(slow_lookup(r))`. The parentheses call `slow_lookup` **now**, in
  the loop's thread; `to_thread` then receives the result, not a function (`TypeError`).
- Awaiting each `to_thread(...)` inside a `for` loop. The loop stays responsive, but the
  lookups still run one after another.
- Replacing `time.sleep` with `await asyncio.sleep` inside `slow_lookup`. You cannot change a
  library you do not own; the whole point is to call it as it is.
- Using `to_thread` for heavy CPU work and expecting a speed-up. The GIL lets only one thread
  run Python code at a time; use a process pool for that.
