## Hint 1

`shutil.make_archive(base_name, format, root_dir=...)` returns the path it created as a `str`. What
is `base_name` (with or without `.zip`)? And what does `shutil.get_archive_formats()` return: names, or
pairs?

## Hint 2

For `archive_members`, open the archive with the right module:
`zipfile.ZipFile(p).namelist()` (skip names ending in `/`) or
`tarfile.open(p).getmembers()` (keep `m.isfile()`, use `m.name`). Remove a leading `"./"`.
For `restore`, call `shutil.unpack_archive(archive, dest)` for zips and add `filter="data"` for tars,
then list `dest.rglob("*")` files as `relative_to(dest).as_posix()`.

## Hint 3

```
archive_formats() = sorted(name for name, desc in shutil.get_archive_formats())
make_backup: if fmt not in archive_formats(): ValueError
             mkdir out_dir; return Path(shutil.make_archive(str(out_dir / name), fmt, root_dir=src_dir))
archive_members:
    if zipfile.is_zipfile(a): names = [n for n in namelist() if not n.endswith("/")]
    elif tarfile.is_tarfile(a): names = [m.name for m in getmembers() if m.isfile()]
    else: ValueError
    return sorted(strip "./" from each)
```
