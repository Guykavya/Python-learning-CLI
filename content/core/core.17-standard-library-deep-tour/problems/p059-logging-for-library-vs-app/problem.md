# Explain: logging in a library versus in an application

Kavya wrote a small library `pricing` that other people install, and an application `shopcli` that
uses it. Her library module starts like this:

```python
# pricing/core.py  (library)
import logging

logging.basicConfig(level=logging.DEBUG, format="%(message)s")
log = logging.getLogger("my_logger")


def total(items):
    log.debug(f"computing total of {len(items)} items")
    try:
        return sum(i["price"] * i["qty"] for i in items)
    except KeyError:
        log.error("bad item")
        print("bad item!")
        raise
```

Users of the library complain: "after `import pricing`, my program suddenly prints debug lines from
**every** library", "my own log format changed", "I can't turn your messages off without turning off
everything", and "when it fails, the log says 'bad item' but not which key or where".

In `answer.md` (about 300 to 450 words), explain:

1. What exactly is wrong with each of the five marked parts: `basicConfig` in a library, the name
   `"my_logger"`, the f-string in `log.debug`, `log.error("bad item")` in the `except` block, and the
   `print`.
2. The rule for **libraries**: what a library should (and should not) do with logging, including what
   `logging.NullHandler` is for.
3. The rule for **applications**: where and when logging is configured, and how the application can
   show `pricing`'s debug messages while keeping every other library at `WARNING` (show the one or two
   lines of code).
4. Why a logger hierarchy based on `__name__` makes question 3 possible (propagation).

Then write the corrected first lines and `except` block of `pricing/core.py` (about 10 lines of code).

**Example of the expected style**

> **`basicConfig` in a library.** `basicConfig` configures the **root** logger, which belongs to the
> application. Running it at import time ...
