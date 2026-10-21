## Approach

An exception object stores the values it was created with in the tuple `args`. `str(err)` is
usually the single message, but it is the `repr` of the key for `KeyError`, and the whole tuple
when there are several arguments. Working from `args` directly gives full control.

## Code

```python
def describe_error(err):
    """Return a one-line description of the exception object err."""
    name = type(err).__name__
    if not err.args:
        return name
    if isinstance(err, KeyError):
        return f"{name}: missing key {err.args[0]}"
    return name + ": " + ", ".join(str(arg) for arg in err.args)
```

## Complexity

O(total length of the arguments).

## Another way

`str(err)` gives the right text for single-argument exceptions other than `KeyError`, so a version
with `if len(err.args) == 1: return name + ": " + str(err)` works for most cases, but needs special
handling for `KeyError` and for several arguments anyway. Using `args` throughout is simpler.
