## Approach

The default is evaluated once, when `def` runs, so a `[]` default would be one list shared by
every call. `None` is immutable and safe to share; it acts as a sentinel meaning "not given".
Inside the body, which runs on every call, `if guests is None: guests = []` creates a fresh list
only when the caller did not supply one.

## Code

```python
def invite(name, guests=None):
    """Append name to guests (a new list if none is given) and return the list."""
    if guests is None:
        guests = []
    guests.append(name)
    return guests
```

## Complexity

O(1) per call (amortised append).

## Another way

Some code writes `guests = [] if guests is None else guests`. It is the same test as a
conditional expression. Avoid `guests = guests or []`: like `if not guests`, it replaces a
caller's empty list.
