# deque(maxlen=n): the last n lines of a file

The Unix tool `tail` prints the last lines of a file. The obvious Python version,
`f.readlines()[-n:]`, loads the **whole file** into memory first: fine for 1 KB, a disaster for a
20 GB log. A `deque` with a `maxlen` keeps only the newest `n` items: when it is full, adding one
on the right silently drops one on the left. One pass, and memory stays at `n` lines.

Write two functions in `solution.py`.

1. `last_n(items: Iterable[str], n: int) -> list[str]`
   - Return the last `n` items of any iterable (a list, a generator, an open file), oldest first.
   - Read the input **once**, from start to end, and never hold more than `n` items.
   - `n == 0` gives `[]`. A negative `n` raises `ValueError`.
2. `tail(path: str | Path, n: int = 10) -> list[str]`
   - The last `n` lines of a UTF-8 text file, **without** their line endings.
   - Both `\n` and Windows `\r\n` endings must be removed. A last line without any ending is still a line.
   - Use `last_n` to do the work.

**Example**

```python
last_n(["a", "b", "c", "d"], 2)        # ['c', 'd']
last_n((x for x in "hello"), 3)        # ['l', 'l', 'o']
last_n(["a"], 5)                       # ['a']

# app.log contains:  "start\nload\nrun\nstop\n"
tail("app.log", 2)                     # ['run', 'stop']
```
