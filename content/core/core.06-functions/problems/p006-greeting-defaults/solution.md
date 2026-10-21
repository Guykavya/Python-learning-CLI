## Approach

Defaults go in the `def` line, after the parameter that has none. Binding fills `name` from the
first argument, then any others by position or keyword, then the defaults for whatever is still
empty. An f-string assembles the result.

## Code

```python
def make_greeting(name, greeting="Hello", punctuation="!"):
    """Return '<greeting>, <name><punctuation>'."""
    return f"{greeting}, {name}{punctuation}"
```

## Complexity

O(len of the result) to build the string.

## Another way

`return greeting + ", " + name + punctuation` builds the same string with `+`. The f-string is
easier to read and to change.
