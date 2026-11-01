## Approach

A class decorator gets the finished class. We read the **raw** class dict with `vars(cls)`,
because that is where we can see what each attribute really is:

- A plain function becomes a method only when it is looked up (its `__get__` binds it). If we
  replace it with another plain function (the wrapper), binding still happens, so `self` is
  passed to the wrapper, which passes it on.
- A `classmethod` or `staticmethod` is a descriptor *around* a function. We take the function
  out (`raw.__func__`), wrap it, and put a new descriptor of the same kind around the wrapper.
  Lookup then does exactly what it did before.
- Properties, `cached_property`, nested classes and data are not methods: left alone.

The counts dict is created inside `count_calls`, so each class gets its own; the wrappers keep a
reference to it through their closure.

## Code

```python
import functools
import types


def _counting(func, counts, name):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        counts[name] += 1
        return func(*args, **kwargs)
    return wrapper


def count_calls(cls):
    counts = {}
    for name, raw in list(vars(cls).items()):
        if name.startswith("__") and name.endswith("__"):
            continue
        if isinstance(raw, (classmethod, staticmethod)):
            counts[name] = 0
            kind = type(raw)                      # classmethod or staticmethod
            setattr(cls, name, kind(_counting(raw.__func__, counts, name)))
        elif isinstance(raw, types.FunctionType):
            counts[name] = 0
            setattr(cls, name, _counting(raw, counts, name))
    cls.call_counts = counts
    return cls


def reset_counts(cls):
    for name in cls.call_counts:
        cls.call_counts[name] = 0
```

Why does `getattr` fail? `getattr(Account, "empty")` is a bound method with `__self__` =
`Account`. Wrapping it in a function and storing that function makes it a *normal method*:
`Savings.empty()` now calls the old bound method, which always passes `Account`, and
`acc.empty()` passes `acc` as an extra argument. `getattr(Account, "fee")` is the bare function;
stored back as a plain function, it is bound to instances and receives `self` as `amount`.

## Complexity

The decorator is O(n) for n names in the class. Each call adds O(1) work.

## Another way

The wrapper can look up the dict on the class each time instead of closing over it:

```python
def count_calls(cls):
    cls.call_counts = {}

    def wrap(func, name):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cls.call_counts[name] += 1
            return func(*args, **kwargs)
        return wrapper
    ...
```

Then `reset_counts` may replace the dict (`cls.call_counts = dict.fromkeys(cls.call_counts, 0)`).
The trade-off: a subclass that assigns its own `call_counts` would change what the parent's
wrappers update. A metaclass or `__init_subclass__` could also instrument classes, but they
would affect every subclass automatically; a decorator is opt-in and explicit, which is
usually what you want for a debugging tool.
