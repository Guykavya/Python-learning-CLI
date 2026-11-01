## Hint 1

Which method runs for `p.x = value`? It gets the descriptor (`self`, one object shared by every
`Point`), the instance and the value. Where can you store the value so that each instance has
its own, and under which key? Which method tells the descriptor its own name?

## Hint 2

How do you test "is this a bool"? Do it **before** the `isinstance(value, self.types)` check,
because `isinstance(True, int)` is already `True`.

```
__set__(instance, value):
    if value is a bool and bool is not allowed: bad
    else: bad = not isinstance(value, self.types)
    if bad: raise TypeError(f"{owner}.{name} must be {' or '.join(type names)}, got {type(value).__name__}")
    instance.__dict__[self.name] = value

__get__(instance, owner=None):
    if instance is None: return self
    try: return instance.__dict__[self.name]
    except KeyError: raise AttributeError(...) from None
```
