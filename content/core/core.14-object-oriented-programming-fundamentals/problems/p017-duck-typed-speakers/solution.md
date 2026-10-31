## Approach

Duck typing means: do not ask for the class, just use the behaviour (chapter section 15). EAFP is the
usual way to write it: try, and handle the failure.

The detail that matters is **what** is inside the `try`. If you write

```python
try:
    results.append(thing.speak())
except AttributeError:
    pass
```

then an `AttributeError` from a bug *inside* `speak()` looks exactly like "has no speak", and the bug
disappears silently. Put only the lookup `thing.speak` in the `try`; a bound method is an object, so you
can store it and call it afterwards (section 3).

## Code

```python
def make_noise(things):
    results = []
    for thing in things:
        try:
            speak = thing.speak
        except AttributeError:
            continue
        results.append(speak())
    return results
```

## Complexity

O(n) calls for n things.

## Another way

`speak = getattr(thing, "speak", None)` returns `None` instead of raising when the attribute is
missing; then `if speak is not None: results.append(speak())`. LBYL ("look before you leap") with
`hasattr(thing, "speak")` works too, but it looks the name up twice. The `try/except/else` form is also
nice: the call goes in the `else:` block, which runs only when the `try` did not fail.
