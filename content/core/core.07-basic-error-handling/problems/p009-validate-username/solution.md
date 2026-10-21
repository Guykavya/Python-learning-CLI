## Approach

Each rule is an `if` that raises. The order matters: the type check comes first because every
later check assumes a string; the length check comes before the character loop and before
`name[0]`, which would fail on an empty string. The messages state the rule and the value that
broke it, so the user knows what to change.

## Code

```python
def validate_username(name):
    """Return name if it is a valid username; otherwise raise TypeError or ValueError."""
    if not isinstance(name, str):
        raise TypeError(f"username must be text (str), got {type(name).__name__}")
    if not 3 <= len(name) <= 15:
        raise ValueError(f"username must be 3 to 15 characters long, got {len(name)}")
    for ch in name:
        if not (ch.isalnum() or ch == "_"):
            raise ValueError(f"username may only use letters, digits and _, found {ch!r}")
    if name[0].isdigit():
        raise ValueError("username must not start with a digit")
    return name
```

## Complexity

O(n) in the length of the name.

## Another way

A table of `(test, message)` pairs walked in a loop keeps all rules in one place. With four rules
the plain `if` chain is clearer; with fifteen the table would win.
