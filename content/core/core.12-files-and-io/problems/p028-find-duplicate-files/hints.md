## Hint 1

Which cheap fact about a file lets you rule out most pairs without opening them? Build a dict from that fact to
the list of paths. For which entries of the dict is a second check needed at all?

## Hint 2

```
by_size = {}  size -> [paths]
for p in root.rglob("*"):
    if p.is_file(): by_size.setdefault(p.stat().st_size, []).append(p)
groups = []
for paths in by_size.values():
    if len(paths) < 2: continue
    by_hash = {}   hash -> [relative names]
    for p in paths: by_hash.setdefault(sha256(p.read_bytes()), []).append(relative name)
    keep the lists with len >= 2, sorted
return sorted(groups)
```
