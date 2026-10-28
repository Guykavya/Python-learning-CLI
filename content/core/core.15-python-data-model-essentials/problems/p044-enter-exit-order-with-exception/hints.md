## Hint 1

Work on one function at a time. For each `with`, write the line `enter ...` when it starts. When the body raises, write the `exit` lines from the **innermost** manager outward, and stop writing "exit" lines for outer managers as soon as one inner manager returned a true value: from there on, the outer ones see no exception (`None`).

## Hint 2

For `five` and `six`, think of `yield` as the place where the exception appears. In `five` the generator catches `KeyError`, prints, then `finally` prints; the generator ends normally, so the `with` swallows the exception and `after p` is printed, then `finished normally`. In `six` the `ValueError` is not caught by `except KeyError`, but `finally` still runs, and then the exception escapes.
