## Hint 1

Print `vars(Account)` for the example class. What type is each value? `deposit` is a
`function`, `empty` is a `classmethod` object, `fee` is a `staticmethod` object, `rich` is a
`property`. Each `classmethod`/`staticmethod` object keeps the real function in `.__func__`.

So for a classmethod: take the function out, wrap it, and put it back *inside a new
classmethod*. Why must you loop over `list(vars(cls).items())` instead of `vars(cls).items()`?
(You call `setattr` on the class while looping.)

## Hint 2

```
def count_calls(cls):
    counts = {}
    for name, raw in list(vars(cls).items()):
        if name starts with "__" and ends with "__": skip
        if raw is a classmethod or staticmethod:
            counts[name] = 0
            setattr(cls, name, type(raw)(make_wrapper(raw.__func__, counts, name)))
        elif raw is a plain function (types.FunctionType):
            counts[name] = 0
            setattr(cls, name, make_wrapper(raw, counts, name))
        # everything else: leave alone
    cls.call_counts = counts
    return cls

def make_wrapper(func, counts, name):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        counts[name] += 1
        return func(*args, **kwargs)
    return wrapper
```

`make_wrapper` is a separate function on purpose: a closure created directly in the loop would
see the *last* `name` (late binding).
