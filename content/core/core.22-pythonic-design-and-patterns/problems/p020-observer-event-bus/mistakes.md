- Looping over the live list while handlers remove from it: the handler after a self-removing
  one is skipped.
- Using `list.remove(fn)` for unsubscribe: it removes the *first* equal function, not necessarily the right subscription.
- A bare `except:`, which also swallows `KeyboardInterrupt`; or catching nothing, so one bad handler kills the rest.
- Printing the error instead of returning it. The caller cannot test or react to a print.
- Returning `None` when nothing failed. The statement says an empty list.
- Letting a handler subscribed *during* a publish run in that same publish.
- An unsubscribe that raises when called a second time.
