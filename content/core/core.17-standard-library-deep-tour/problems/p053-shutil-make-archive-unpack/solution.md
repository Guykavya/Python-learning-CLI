## Approach

`make_archive` hides all the walking and writing; we only build `base_name` from `out_dir / name`
without an extension and convert the result to a `Path`. Checking the format against
`get_archive_formats()` gives a clear `ValueError` before anything happens (`make_archive` would also
raise one, but only after creating `out_dir`).

Listing has to deal with the two formats' habits: zips may contain folder entries ending in `/`;
tars from `make_archive` contain `.`, the folders, and names starting with `./`. Keeping only real
files and stripping `./` gives the same list for both formats.

For unpacking, tar archives get `filter="data"`, the safe extraction policy (default since Python
3.14, and a warning in 3.12 and 3.13 if you do not choose one). The zip unpacker has no such option
and would raise `TypeError` if given one.

## Code

```python
import shutil
import tarfile
import zipfile
from pathlib import Path


def archive_formats():
    return sorted(name for name, _description in shutil.get_archive_formats())


def make_backup(src_dir, out_dir, name, fmt="zip"):
    if fmt not in archive_formats():
        raise ValueError(f"unknown archive format {fmt!r}")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    created = shutil.make_archive(str(out_dir / name), fmt, root_dir=src_dir)
    return Path(created)


def _clean(name):
    while name.startswith("./"):
        name = name[2:]
    return name


def archive_members(archive):
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
    elif tarfile.is_tarfile(archive):
        with tarfile.open(archive) as tf:
            names = [m.name for m in tf.getmembers() if m.isfile()]
    else:
        raise ValueError(f"{archive} is not a zip or tar archive")
    return sorted(_clean(n) for n in names)


def restore(archive, dest):
    dest = Path(dest)
    if zipfile.is_zipfile(archive):
        shutil.unpack_archive(archive, dest)
    else:
        shutil.unpack_archive(archive, dest, filter="data")
    return sorted(p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file())
```

## Complexity

O(total bytes) to compress or extract; O(F log F) to sort F names.

## Another way

`zipfile` and `tarfile` give you full control (exact member names, no folder entries, per-file
compression, adding files from memory); `shutil` gives you one-line convenience. A backup tool that
must produce **identical** archives on every machine usually uses `zipfile` directly. From Python 3.12,
`name.removeprefix("./")` strips one prefix in a single call.
