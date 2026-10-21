## Approach

Each step is `data = data[key]`. A missing dict key raises `KeyError` and a bad list index raises
`IndexError`; both are `LookupError`s, so one clause handles both. A step that is impossible
because of the type raises `TypeError`, which is not a `LookupError` and so propagates by itself.
Here the `try` wraps the loop, because every line in it is a lookup and all share one response.

## Code

```python
def dig(data, keys, default=None):
    """Follow keys into nested data; return default if a key or index is missing."""
    try:
        for key in keys:
            data = data[key]
    except LookupError:
        return default
    return data
```

## Complexity

O(k) for k keys.

## Another way

`except (KeyError, IndexError):` is equivalent here and lists exactly what is expected. Using the
family class says "any failed lookup", which also covers lookup errors from other container
types you may meet later.
