- `LifoQueue: c b` vs `b c`: the newest item comes out first, and the two `get()` calls run left
  to right inside the `print`.
- Putting `urgent` before `also urgent`. Equal priorities fall back to comparing the strings,
  not to insertion order.
- Printing `z added`. `put_nowait` raised before that line ran.
- Writing `Full raised, size 3`. The failed `put_nowait` added nothing.
- Expecting `get(timeout=0.01)` to return `None`. A timeout raises `queue.Empty`, the same as
  `get_nowait()`.
- Writing `full? True` for the unbounded queue. `maxsize=0` means it can never be full.
