## Approach

A reference count is only meaningful as a *difference* on an object nobody else knows about.
`object()` gives a fresh, mortal object whose only reference is our local variable. Both
readings use the same expression, so whatever temporary references the call adds (or borrows)
on this Python version appear in both and cancel. Holding `kept` between the readings is the
whole trick: without it the container is freed before the second count.

## Code

```python
import sys


def extra_refs(store):
    obj = object()
    before = sys.getrefcount(obj)
    kept = store(obj)
    after = sys.getrefcount(obj)
    del kept
    return after - before
```

## Complexity

O(1) plus whatever `store` does.

## Another way

You can see the references themselves instead of counting them: `gc.get_referrers(obj)` returns
the container objects that point at `obj` (only containers tracked by the garbage collector, so
it is a debugging aid, not a precise counter). Usually you do not need counts at all. The
question "is this object still alive?" is better answered with `weakref.ref`, which works the
same on every Python version and on implementations without reference counting, such as PyPy.

**Version note.** On 3.11 `sys.getrefcount(obj)` for a local is typically 2 (the variable plus
the call's argument). On 3.14 it can be 1, because the interpreter borrows the local's reference.
Immortal objects (3.12+) report a huge constant. None of this matters for the difference.
