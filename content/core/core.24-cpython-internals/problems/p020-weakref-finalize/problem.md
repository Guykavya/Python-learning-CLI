# Clean up with weakref.finalize

Some objects own something that must be released: a temporary file, a lock, a connection. The
right way is an explicit `close()` (or a `with` block). But if someone forgets, it is nice to clean
up anyway when the object is garbage collected.

`__del__` can do that, but it has traps (it runs at unpredictable times, exceptions in it are
only printed, and it can bring the object back to life). The standard library offers a safer tool:

```python
fin = weakref.finalize(obj, func, *args)
```

registers `func(*args)` to be called **once**, when `obj` is garbage collected, or earlier if you
call `fin()` yourself. `fin.alive` is `True` until it has run. The finalizer holds only a *weak*
reference to `obj`, so registering it does not keep `obj` alive. But it holds `func` and `args`
**strongly**, so they must not refer to `obj` (a bound method like `obj.cleanup` does).

`weakref.WeakSet()` is a set that holds its items weakly: an item disappears from the set when it is
garbage collected.

Copy `starter.py` to `solution.py` and finish `TempResource` and `live_resources`.

**`TempResource(name, log)`**:

- on creation appends `"open <name>"` to the list `log`;
- appends `"close <name>"` to `log` **exactly once**: on `close()`, at the end of a `with` block,
  or when the object is garbage collected without having been closed;
- has a read-only property `closed`;
- `close()` may be called any number of times;
- `with TempResource(...) as r:` gives the resource itself as `r`.

**`live_resources()`** returns the sorted names of all `TempResource` objects that still exist
and are not closed (use a module-level `WeakSet`).

**Example**

```python
log = []
r = TempResource("tmp1", log)
live_resources()     # ['tmp1']
del r                # the last reference is gone
log                  # ['open tmp1', 'close tmp1']
live_resources()     # []

with TempResource("tmp2", log) as r2:
    r2.closed        # False
r2.closed            # True
r2.close()           # does nothing the second time
log[-2:]             # ['open tmp2', 'close tmp2']
```

(CPython frees the object at the `del` because its reference count drops to zero. Other Python
implementations may clean up later, at the next garbage collection; that is why the tests call
`gc.collect()` before they check.)
