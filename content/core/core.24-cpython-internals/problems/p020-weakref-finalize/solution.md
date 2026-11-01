## Approach

`weakref.finalize` already provides everything the task asks for:

- it calls the callback when the object is collected;
- calling the finalizer object runs the callback now, and **only the first call** does anything;
- `.alive` says whether it has run.

So `close()` just calls the finalizer, and `closed` is `not finalizer.alive`. The callback is a
module-level function that receives only the name and the log. The finalizer keeps a weak
reference to the resource but strong references to the callback and arguments; if they referred
to the resource, the resource could never be collected.

A `WeakSet` remembers all instances without keeping any of them alive.

## Code

```python
import weakref

_instances = weakref.WeakSet()


def _release(name, log):
    log.append(f"close {name}")


class TempResource:
    def __init__(self, name, log):
        self.name = name
        log.append(f"open {name}")
        self._finalizer = weakref.finalize(self, _release, name, log)
        _instances.add(self)

    def close(self):
        self._finalizer()

    @property
    def closed(self):
        return not self._finalizer.alive

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


def live_resources():
    return sorted(r.name for r in list(_instances) if not r.closed)
```

`list(_instances)` takes a snapshot first, so collection during the loop cannot change the set
while we iterate.

## Complexity

O(1) for creating and closing. `live_resources` is O(n log n) for n live instances.

## Another way

With `__del__`:

```python
class TempResource:
    def __init__(self, name, log):
        self.name, self.log, self._closed = name, log, False
        log.append(f"open {name}")

    def close(self):
        if not self._closed:
            self._closed = True
            self.log.append(f"close {self.name}")

    def __del__(self):
        self.close()
```

It passes the tests on CPython (since Python 3.4, PEP 442, even objects in cycles that have
`__del__` are collected). But `__del__` may see a half-built object if `__init__` raised, exceptions
inside it are only printed, and at interpreter exit it may run when modules are already torn down.
`finalize` avoids all of that and also runs at exit for objects still alive (`fin.atexit` is `True`
by default).
