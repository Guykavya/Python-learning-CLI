## Approach

`**details` collects the extra keyword arguments into a **new** dict on every call, in the
order they were written. Even when the caller writes `**extra`, `details` is a fresh dict, so
nothing we do can change `extra`. Build the result with `"name"` first, then copy the details
that are not `None`.

## Code

```python
def build_profile(name, **details):
    """Return a new dict with 'name' first, then every detail whose value is not None."""
    profile = {"name": name}
    for key, value in details.items():
        if value is not None:
            profile[key] = value
    return profile
```

## Complexity

O(k) for k keyword arguments.

## Another way

A dict comprehension (core.05) for the details, merged with the pipe operator:
```python
return {"name": name} | {k: v for k, v in details.items() if v is not None}
```
