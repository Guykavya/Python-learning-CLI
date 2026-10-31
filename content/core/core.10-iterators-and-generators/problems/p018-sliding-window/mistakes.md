- Calling `list(iterable)` and slicing `data[i:i + k]`. It is correct for lists but hangs on
  an endless stream and cannot work on a generator that you can read only once.
- Yielding a **list** that you then change. The caller ends up with many references to the
  same list, all showing the last window. Yield a tuple or a fresh copy.
- Yielding before the window is full, so the first windows are shorter than `k`.
- Off by one: `len(window) >= k` before you drop the oldest item gives windows of size `k + 1`.
