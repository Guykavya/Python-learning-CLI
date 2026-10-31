# Temporarily change environment variables

Tests and scripts often need an environment variable to have a certain value **for a short time**
(for example `TZ`, `DEBUG` or `HOME`) and must leave the program in its old state afterwards. Write
the context manager `temp_env(**changes)` in `solution.py` with `@contextlib.contextmanager`.

- `with temp_env(DEBUG="1", MODE="fast"):` sets those variables in `os.environ` for the block.
- Values that are not strings are converted with `str()` (`os.environ` only accepts strings).
- A value of `None` **removes** the variable inside the block.
- When the block ends, **normally or because of an exception**, every named variable is back to the
  state it had before: the old value if there was one, absent if there was none. The exception
  continues to propagate.
- Variables not named are never touched. If setting one of the variables fails, the ones already
  changed are still restored.
- It yields `os.environ`. Nested uses work (the inner block restores the outer block's value).

**Example**

```python
import os

os.environ["MODE"] = "slow"
with temp_env(MODE="fast", DEBUG=1):
    os.environ["MODE"]       # 'fast'
    os.environ["DEBUG"]      # '1'
os.environ["MODE"]           # 'slow'
"DEBUG" in os.environ        # False
```
