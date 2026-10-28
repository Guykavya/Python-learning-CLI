## Hint 1

To restore a variable afterwards you must know what it was **before**. What does `os.environ.get(name)` return for a variable that does not exist? So how can one saved value mean both "was set to X" and "did not exist"?

## Hint 2

Save first: `saved = {name: os.environ.get(name) for name in changes}`. Then `try:` set everything, `yield`, and in `finally:` loop over `saved`: `None` -> `os.environ.pop(name, None)`, otherwise `os.environ[name] = old`. Put the setting loop **inside** the `try`, so a failure halfway still restores.

## Hint 3

```
saved = {n: os.environ.get(n) for n in changes}
try:
    for n, v in changes.items(): if v is None: pop(n, None) else: environ[n] = str(v)
    yield os.environ
finally:
    for n, old in saved.items(): if old is None: pop(n, None) else: environ[n] = old
```
