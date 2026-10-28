# Parse command-line arguments

A command-line tool reads its settings from `sys.argv`. The `argparse` module does the hard work.

Write `parse_args(argv)` in `solution.py`. It takes a **list of strings** (not `sys.argv`, so it can be
tested) and returns the `Namespace` from an `ArgumentParser(prog="tidy")` that accepts:

- one or more positional `paths` (at least one is required);
- `--verbose` or `-v`: a flag, `False` unless given;
- `--limit N`: an integer, default `10`;
- `--mode`: either `copy` or `move`, default `copy`.

Wrong usage (no paths, `--limit abc`, `--mode zip`) makes argparse exit with status 2, as usual.

**Example**

```python
ns = parse_args(["a.txt", "b.txt", "-v", "--limit", "3"])
ns.paths     # ['a.txt', 'b.txt']
ns.verbose   # True
ns.limit     # 3
ns.mode      # 'copy'
```
