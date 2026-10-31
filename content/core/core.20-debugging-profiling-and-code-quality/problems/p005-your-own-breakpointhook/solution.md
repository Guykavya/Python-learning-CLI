## Approach

`breakpoint()` is a tiny built-in: it calls `sys.breakpointhook(*args, **kwargs)` and returns
what the hook returns. The default hook reads `PYTHONBREAKPOINT` and starts pdb. So installing
a recorder is just assigning a function to `sys.breakpointhook`.

Inside the hook we need the **caller**. `sys._getframe(n)` walks `n` frames out from the
current one. Frame 0 is the hook, and since `breakpoint` is written in C it has no Python frame,
so frame 1 is the function that wrote `breakpoint()`.

The locals must be **copied**. `frame.f_locals` is not a normal snapshot:

- In Python 3.11 and 3.12 it is a dict that the frame **reuses and refreshes**. Store it twice
  and both records are the same object, showing only the latest values.
- From Python 3.13 it is a live **proxy** (PEP 667) that always shows the current values.

`dict(frame.f_locals)` freezes the values at that moment (a shallow copy: a list variable is
still the same list object).

## Code

```python
import sys


def install_recorder() -> list[dict]:
    records: list[dict] = []

    def hook(*args, **kwargs):
        frame = sys._getframe(1)
        records.append({"function": frame.f_code.co_name, "locals": dict(frame.f_locals)})

    sys.breakpointhook = hook
    return records


def uninstall() -> None:
    sys.breakpointhook = sys.__breakpointhook__
```

## Complexity

Each `breakpoint()` costs O(v) to copy v local variables.

## Another way

`inspect.currentframe().f_back` is the same frame as `sys._getframe(1)` and reads a little
more clearly. In real life you rarely write a hook: set the environment variable instead, for
example `PYTHONBREAKPOINT=0` (do nothing) or `PYTHONBREAKPOINT=mymodule.myhook` (call your
function). A recorder like this is handy for "print debugging without prints" in code you
cannot attach a debugger to, such as a test run on a server.
