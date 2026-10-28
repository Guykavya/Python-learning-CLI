# Open many files at once with `ExitStack`

`with open(a) as f1, open(b) as f2:` works when you know **how many** files there are. For a
list of paths of unknown length you cannot write that line. `contextlib.ExitStack` solves it: it is
a context manager that collects other context managers, and on exit closes **all** of them, in
reverse order, even when something failed halfway.

```python
from contextlib import ExitStack

with ExitStack() as stack:
    files = [stack.enter_context(open(p)) for p in paths]
    ...        # all files are open here
# all files are closed here, even if the 3rd open() raised
```

Write two functions in `solution.py`. Both open **all** the files **at the same time** (use the
built-in name `open` and an `ExitStack`) and close them before returning.

- `read_all(paths)` returns a list with the whole text of each file, in the order of `paths`.
- `merge_lines(paths)` reads the files side by side: it returns a list of tuples, where tuple `i` has
  line `i` of every file, with the trailing newline removed. It stops at the shortest file (use `zip`).

If one of the paths does not exist, `FileNotFoundError` propagates, and every file opened before it is
closed. No paths gives `[]`.

**Example**

```python
# a.txt: "a1\na2\n"    b.txt: "b1\nb2\nb3\n"
read_all(["a.txt", "b.txt"])        # ['a1\na2\n', 'b1\nb2\nb3\n']
merge_lines(["a.txt", "b.txt"])     # [('a1', 'b1'), ('a2', 'b2')]
```
