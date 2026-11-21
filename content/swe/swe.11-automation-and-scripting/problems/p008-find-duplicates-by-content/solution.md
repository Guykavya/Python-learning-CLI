## Approach

```python
def sha256_of(path, chunk=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def find_duplicates(root, min_size=1):
    by_size = {}
    for p in Path(root).rglob("*"):
        if p.is_file() and not p.is_symlink() and p.stat().st_size >= min_size:
            by_size.setdefault(p.stat().st_size, []).append(p)
    groups = []
    for paths in by_size.values():
        if len(paths) > 1:
            by_hash = {}
            for p in paths:
                by_hash.setdefault(sha256_of(p), []).append(p)
            groups += [sorted(g) for g in by_hash.values() if len(g) > 1]
    return sorted(groups)
```

The size filter is what makes the tool usable: in a typical folder most sizes are unique, so most files are never read at all. Hashing in chunks keeps memory flat whatever the file size. Sorting both levels makes the output identical on every run, which makes it testable and diffable.

## Complexity

Pass one is O(n) `stat` calls. Pass two reads only files with a shared size: O(total bytes of those files). Memory is O(n) for the dictionaries plus one chunk.

## Another way

Add a middle step for large files: hash only the first 4 KB of each same-size file, and fully hash only those whose first blocks agree. Duplicate finders such as `fdupes` do this, and on a photo library it avoids reading most of the bytes. A SHA-256 match is treated as equality; if you need certainty, compare the bytes of a matching pair with `filecmp.cmp(a, b, shallow=False)` before deleting anything.
