## Approach

Each function depended on a hidden collaborator (clock, random generator, file system). We turn
each into a parameter whose default is the real one. Production code calls the functions as
before; tests pass a fake. The function body only talks to the parameter.

## Code

```python
import random
from datetime import datetime


def make_greeting(name, now=datetime.now):
    hour = now().hour
    if hour < 12:
        return f"Good morning, {name}"
    if hour < 18:
        return f"Good afternoon, {name}"
    return f"Good evening, {name}"


def is_expired(token, now=datetime.now):
    return now() >= token["expires"]


def pick_tip(tips, rng=random):
    return rng.choice(tips)


def save_report(rows, path, opener=open):
    with opener(path, "w") as f:
        for name, score in rows:
            f.write(f"{name},{score}\n")
```

## Complexity

Same as before: O(1) for the first three, O(rows) for `save_report`. Injection costs nothing at
run time.

## Another way

Use `None` as the default and look up the real thing in the body:

```python
def pick_tip(tips, rng=None):
    rng = rng or random
    return rng.choice(tips)
```

This is useful when the real object might change after import (for example a clock a test
framework replaces). The price is one extra line. For a stable default such as `open`,
`random` or `datetime.now`, putting it straight in the signature is shorter and shows the
default to anyone reading `help(func)`.

For many functions that share the same collaborators, group them in a class and inject once in
`__init__` (see p026).
