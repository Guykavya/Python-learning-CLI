- **Clearing the whole cache when it is full.** Memory is bounded, but every busy line has to be
  parsed again right after each clear. Drop one entry at a time.
- **Dropping the oldest *inserted* line instead of the least recently *used*.** A line used every
  second would be thrown out just because it was added early. Move a line to the end on every hit.
- **`close()` that only clears `seen`.** The list gets empty, but the widget itself is still
  held by the bus, and so is every widget ever made.
- **`self._handlers.remove(handler)` without checking.** It raises `ValueError` on a second
  `close()` or for an unknown handler.
- **Looping over the live list in `publish`.** Removing an item during the loop skips the next
  handler, a bug that only shows up when a handler unsubscribes itself.
- **Using `is` to find the bound method.** `self.on_event is self.on_event` is `False` (a new
  object each time); `==` (which `in` and `remove` use) is `True`.
- **Looking for a leak with `sys.getsizeof`.** It does not follow references. Compare
  `tracemalloc` snapshots, or check with `weakref` whether an object you expect to be gone is
  still alive.
