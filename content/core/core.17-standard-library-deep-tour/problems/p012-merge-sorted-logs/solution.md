## Approach

`heapq.merge` keeps a small heap with **one** pending item per input. It yields the smallest,
then pulls the next item from the input it came from. Because each input is already sorted,
that is enough to produce a fully sorted stream, and it never reads more than one item ahead
per input. It is also **stable**: on equal keys the earlier input wins.

Two details make it correct for logs:

- `key=timestamp` (the first 19 characters). Without a key, whole lines are compared, so at the
  same second `"... aaa"` from the second server would jump ahead of `"... zzz"` from the first.
- For files, each line is stripped of its `"\n"` before merging, and blank lines are dropped. Then
  writing `line + "\n"` gives every line exactly one ending, even when an input's last line had none.

All input files stay open while the merge runs (it is lazy!), so they are closed in a `finally`.

## Code

```python
import heapq
from collections.abc import Iterable, Iterator
from pathlib import Path


def timestamp(line: str) -> str:
    return line[:19]


def merge_logs(*sources: Iterable[str]) -> Iterator[str]:
    return heapq.merge(*sources, key=timestamp)


def clean_lines(f) -> Iterator[str]:
    for line in f:
        line = line.rstrip("\n")
        if line.strip():
            yield line


def merge_files(paths: list[Path], out_path: Path) -> int:
    files = [open(path, encoding="utf-8") for path in paths]
    try:
        count = 0
        with open(out_path, "w", encoding="utf-8") as out:
            for line in merge_logs(*(clean_lines(f) for f in files)):
                out.write(line + "\n")
                count += 1
    finally:
        for f in files:
            f.close()
    return count
```

ISO timestamps (`YYYY-MM-DDTHH:MM:SS`) sort correctly as strings because every field has a fixed
width and the biggest unit comes first. That is why the key can be a plain slice.

## Complexity

O(N log k) time for N lines in k sources, O(k) memory for the merge itself.

## Another way

`sorted(itertools.chain(*sources), key=timestamp)` gives the same order (Python's sort is
stable too), but it reads everything into memory first: O(N) memory and no output until the end.
`contextlib.ExitStack` (core.12-style context managers) is a neat way to open a variable number of
files in one `with` statement instead of the `try`/`finally`.
