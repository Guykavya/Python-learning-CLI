## Hint 1

Split the work: first turn each text into a clean dict `{normalised name: version}`, then compare
two dicts. Which set operations give "only in new", "only in old" and "in both"? Why must you never
compare `"3.10"` and `"3.9"` as strings?

## Hint 2

```text
normalise: lowercase; for each char: if it is - _ or . -> add "-" unless the last added char is "-"

parse_freeze: for number, line in enumerate(lines, start=1):
    strip; skip "", "#...", "-..."
    "==" in line  -> name, version
    " @ " in line -> name, "@ " + url
    else -> ValueError(f"line {number}: ...")
    duplicate normalised name -> ValueError

as_numbers(v): parts = v.split("."); all digits? -> ints, drop trailing zeros, tuple; else None

diff: for name in sorted(old.keys() | new.keys()):
    only new -> added; only old -> removed
    both and different text -> as_numbers both: None? changed : compare tuples (equal -> nothing)
```
