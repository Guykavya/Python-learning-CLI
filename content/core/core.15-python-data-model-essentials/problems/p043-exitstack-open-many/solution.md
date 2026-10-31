## Approach

`ExitStack` is a context manager whose contents are decided at run time. Each `enter_context` call pushes one more clean-up onto an internal stack; leaving the `with` pops and runs them in reverse order. Because the stack is registered **before** the next file is opened, a failure in the third `open` still closes the first two: when the exception travels out of the `with ExitStack()` block, `ExitStack.__exit__` runs and closes whatever was registered so far.

The return statements are inside the block because `zip` and file iteration are lazy; materialising the list before the files close avoids reading from closed files.

## Code

```python
from contextlib import ExitStack


def read_all(paths):
    """Open all files at once, read each, and return the list of contents."""
    with ExitStack() as stack:
        files = [stack.enter_context(open(path)) for path in paths]
        return [f.read() for f in files]


def merge_lines(paths):
    """Open all files at once and return the lines side by side, stopping at the shortest file."""
    with ExitStack() as stack:
        files = [stack.enter_context(open(path)) for path in paths]
        return [tuple(line.rstrip("\n") for line in lines) for lines in zip(*files)]
```

## Complexity

O(total size of the files) time; memory is O(total output).

## Another way

For a fixed small number of files, a single `with open(a) as f, open(b) as g:` is clearer. `ExitStack` is the tool when the number is dynamic, or when some resources are optional (`if need_log: stack.enter_context(open(log))`).
