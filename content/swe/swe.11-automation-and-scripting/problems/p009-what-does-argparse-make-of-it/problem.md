# What does argparse make of it?

Chapter sections 3 (the `tidy` parser) and 3.1 (argparse in one table). Before you trust a command line in a cron job, you should be able to say what the parser will do with it **without running it**. This is the `tidy` parser of problem p004:

```python
import argparse
from pathlib import Path


def build_parser():
    p = argparse.ArgumentParser(prog="tidy", description="Tidy a folder safely.")
    p.add_argument("-v", "--verbose", action="count", default=0)
    p.add_argument("--version", action="version", version="tidy 1.0")
    sub = p.add_subparsers(dest="command", required=True)
    org = sub.add_parser("organize")
    org.add_argument("folder", type=Path)
    org.add_argument("-n", "--dry-run", action="store_true")
    und = sub.add_parser("undo")
    und.add_argument("folder", type=Path)
    dup = sub.add_parser("dupes")
    dup.add_argument("folder", type=Path)
    dup.add_argument("--min-size", type=int, default=1, metavar="BYTES")
    return p
```

Each line below is typed after `python tidy.py` in a shell (so the quotes are removed by the shell before Python sees the words). For each one, decide what `build_parser().parse_args(...)` gives.

1. `-vv organize x`
2. `organize --dry-run`
3. `dupes x --min-size abc`
4. `dupes --min-size 0 x`
5. `organize x -v`
6. `organize -n "old photos"`

## Answer format

One line per command, starting with its number, a colon and a space. Then either:

- `exit 2` if argparse refuses the line (it prints a usage error and raises `SystemExit(2)`), or
- every attribute of the resulting `Namespace`, **sorted by name**, as `name=value` separated by single spaces, where `value` is what `str()` prints (so a `Path("x")` is written `x`, booleans `True`/`False`).

For example, `undo y` would be:

```text
0: command=undo folder=y verbose=0
```

Write lines 1 to 6 in `answer.txt`.

## After you answer

- Line 5 and line 1 both use `-v`. Why does one work and the other fail? How would you change the parser if you wanted `-v` to be accepted in both places?
- In line 3, which object turns `"abc"` into an error, and why is that better than letting your own code do `int(args.min_size)` later?
