# Inject the collaborators

`starter.py` has four small functions that quietly reach out to the world:

- `make_greeting(name)` asks the real clock for the hour.
- `is_expired(token)` asks the real clock whether `token["expires"]` has passed.
- `pick_tip(tips)` asks the real `random` module for a tip.
- `save_report(rows, path)` opens a real file.

They work, but you cannot test them: the answer depends on the time of day, on luck, or on the
disk. These hidden helpers are called **collaborators**. The fix is **dependency injection**:
the caller *hands in* the collaborator, and the default is the real one.

Copy `starter.py` to `solution.py` and add one parameter to each function. Keep the old
behavior when the parameter is left out.

| Function | New parameter | What it is | Default |
|---|---|---|---|
| `make_greeting(name, now=...)` | `now` | a function with no arguments that returns a `datetime` | `datetime.now` |
| `is_expired(token, now=...)` | `now` | the same | `datetime.now` |
| `pick_tip(tips, rng=...)` | `rng` | any object with a `.choice(seq)` method | the `random` module |
| `save_report(rows, path, opener=...)` | `opener` | a function like `open(path, mode)` that returns a file object | `open` |

Rules:

- Inside the four function bodies there must be **no direct call** to `datetime.now()`, no use
  of `random.<anything>`, and no call to `open(...)`. Only use the parameters.
- `now` is **called** every time it is needed (it is a function, not a stored `datetime`).
- `save_report` calls `opener(path, "w")`, writes one `name,score` line per row (each line ends
  with `"\n"`), and closes the file.

**Example**

```python
from datetime import datetime

make_greeting("Ana", now=lambda: datetime(2024, 5, 17, 9, 30))   # 'Good morning, Ana'
pick_tip(["a", "b", "c"], rng=FakeRandom())                        # whatever FakeRandom.choice returns
```

Tests pass fakes (a clock stuck at 09:30, a "random" that always picks the last item, an
opener that returns an in-memory file), so they are fast and never flaky.
