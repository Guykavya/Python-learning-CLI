## Hint 1

Look at what changes between runs of `make_greeting("Ana")`: the answer depends on something
the function *fetches by itself*. What if the caller could pass that "something" in? What
should the default be so that old callers keep working?

## Hint 2

Put the real thing in the default value and call the parameter instead of the global:

```python
def make_greeting(name, now=datetime.now):
    hour = now().hour
    ...

def pick_tip(tips, rng=random):
    return rng.choice(tips)

def save_report(rows, path, opener=open):
    with opener(path, "w") as f:
        ...
```

`datetime.now` without brackets is the *function itself*. Writing `now=datetime.now()` would
call it once, when the function is defined, and freeze the time forever.
