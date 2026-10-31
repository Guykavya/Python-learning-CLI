## Approach

`redirect_stdout` replaces `sys.stdout` for the time of the `with` block and puts the old object back when the
block ends, also after an error. Because `print` looks up `sys.stdout` every time it runs, it writes into the
`StringIO`. Read the text with `getvalue()` after the block.

## Code

```python
import io
from contextlib import redirect_stderr, redirect_stdout


def capture_output(func, *args, **kwargs):
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        result = func(*args, **kwargs)
    return result, out.getvalue(), err.getvalue()
```

## Complexity

O(size of the printed text) memory.

## Another way

Write the swap by hand: `old = sys.stdout; sys.stdout = out; try: ... finally: sys.stdout = old`. That is what
`redirect_stdout` does for you. Never forget the `finally`.
