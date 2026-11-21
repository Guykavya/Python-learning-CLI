## Hint 1

Two passes. Pass one: walk the tree and build a dictionary `size -> [paths]` (cheap: `stat()` only). Which sizes can contain duplicates? Pass two: for those only, build `hash -> [paths]`. For the chunked reading: what does `f.read(chunk)` return at the end of the file, and how can a `while` loop stop on it?

## Hint 2

```text
sha256_of: h = hashlib.sha256(); open "rb"; while block := f.read(chunk): h.update(block); return h.hexdigest()
find_duplicates:
    by_size = {}
    for p in Path(root).rglob("*"):
        if p.is_file() and not p.is_symlink() and p.stat().st_size >= min_size:
            by_size.setdefault(size, []).append(p)
    groups = []
    for paths in by_size.values() with len > 1:
        by_hash = {}; for p in paths: by_hash.setdefault(sha256_of(p), []).append(p)
        groups += [sorted(g) for g in by_hash.values() if len(g) > 1]
    return sorted(groups)
```
