- Checking `isinstance(listener, SomeBaseClass)`. The task is duck typing: any object with a
  callable `handle` is fine.
- `hasattr(listener, "handle")` only. A string attribute called `handle` passes that check but cannot
  be called.
- Stopping at the first failing listener, or raising inside the loop. Everyone must run first.
- Catching `BaseException`. That would also swallow `KeyboardInterrupt` and `SystemExit`.
- Looping over `self._listeners[name]` directly. A listener that unsubscribes itself shifts the list,
  and the loop skips the next listener.
- Using `listener in group` for the duplicate check. `in` uses `==`; the task means the same object
  (`is`).
- Wrapping the error in a new exception with the note in the message. Keep the original exception and
  use `add_note`.
