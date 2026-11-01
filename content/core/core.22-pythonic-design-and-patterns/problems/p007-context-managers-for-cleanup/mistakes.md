- Putting the restore after `yield` without `finally`: an exception skips it and the setting stays changed.
- `__exit__` returning `True` by accident (or `except: pass` around the yield): it swallows the caller's error.
- Using `copy_text` with two nested `with` blocks and calling it done: it works, but the task asks for one
  `with a as x, b as y` line.
- Forgetting the "attribute did not exist" case: restoring `None` leaves a new attribute behind.
- Opening the resource **before** the `with` (`r = open_resource(name)` then `with r:`) and the
  `with` only guards part of the work.
- Writing `@contextmanager` on a function that never `yield`s, or that yields twice.
