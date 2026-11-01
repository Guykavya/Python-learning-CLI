## Approach

`with` calls `__enter__` when the block starts and `__exit__` when it ends, **always**, including
when an exception flies out. That is the whole point: the cleanup cannot be skipped or forgotten.

- `with a as x, b as y:` is the same as nesting two `with`s. If opening `b` fails, `a` is closed
  first, because its block has already started.
- `@contextmanager` turns a generator into a context manager: code before `yield` is the
  set-up, the `yield` is the body of the `with`, code after it is the tear-down. Put the tear-down
  in `finally` so an exception raised at the `yield` does not skip it.
- `temp_setting` needs a marker for "attribute did not exist". `object()` is a perfect unique marker.

## Code

```python
from contextlib import contextmanager


def read_all(open_resource, name):
    with open_resource(name) as r:
        return r.read()


def copy_text(open_resource, src, dst):
    with open_resource(src) as s, open_resource(dst) as d:
        text = s.read()
        d.write(text)
        return len(text)


def run_locked(lock, func):
    with lock:
        return func()


@contextmanager
def temp_setting(obj, name, value):
    missing = object()
    old = getattr(obj, name, missing)
    setattr(obj, name, value)
    try:
        yield
    finally:
        if old is missing:
            delattr(obj, name)
        else:
            setattr(obj, name, old)


def format_with_precision(cfg, numbers, precision):
    with temp_setting(cfg, "precision", precision):
        return [cfg.fmt(n) for n in numbers]
```

Note `return` inside `with` is fine: the tear-down runs after the return value is computed.

## Complexity

No change: O(1) extra work per `with`. The benefit is safety: no leaked files or locks.

## Another way

`temp_setting` as a class with `__enter__` (save and set) and `__exit__` (restore, `return False`
so errors propagate). `contextlib.closing(thing)` makes `with` work for objects that only have
`close()`. `contextlib.ExitStack` handles "open an unknown number of resources".
