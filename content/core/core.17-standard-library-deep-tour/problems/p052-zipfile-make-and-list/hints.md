## Hint 1

For each file found by `src.rglob("*")`, which name should it have *inside* the archive? What does
`path.relative_to(src).as_posix()` give? For safety: which parts of `PurePosixPath("a/../../x").parts`
show that the path climbs out of the folder?

## Hint 2

Open with `zipfile.ZipFile(dest_zip, "w", compression=zipfile.ZIP_DEFLATED)` in a `with` block and
call `zf.write(path, arcname=...)`. Skip `dest_zip` when `path.resolve() == dest_zip.resolve()`.
In `safe_extract`, loop over **all** `zf.namelist()` and raise before calling `zf.extractall(dest)`.

## Hint 3

```
is_safe_name(name):
    if name starts with "/" or "\" or "\" in name: unsafe
    parts = PurePosixPath(name).parts
    if parts and ":" in parts[0]: unsafe          # C:/...
    return ".." not in parts

safe_extract(zip_path, dest):
    with ZipFile(zip_path) as zf:
        for name in zf.namelist(): if not safe: raise ValueError
        zf.extractall(dest)
    return sorted file names
```
