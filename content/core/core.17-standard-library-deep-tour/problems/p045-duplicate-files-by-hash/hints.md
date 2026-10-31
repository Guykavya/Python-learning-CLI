## Hint 1

What can you learn about a file without opening it? If only one file has size 1000, can it have a
duplicate? Which data structure maps "a size" to "all files of that size"?

## Hint 2

Use `defaultdict(list)` twice: first `size -> [paths]` (skip size 0), then, inside each size group
with two or more files, `hash -> [relative paths]`. Keep only hash groups with two or more names.
Remember to call `file_hash(path)` by that name.

## Hint 3

```
by_size = defaultdict(list)
for path in root.rglob("*"): if file and size > 0: by_size[size].append(path)
groups = []
for paths in by_size.values():
    if len(paths) < 2: continue
    by_hash = defaultdict(list)
    for p in paths: by_hash[file_hash(p)].append(p.relative_to(root).as_posix())
    groups += [sorted(names) for names in by_hash.values() if len(names) >= 2]
return sorted(groups)
```
