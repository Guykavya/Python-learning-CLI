## Approach

**Writing.** Collect the files with `rglob`, sort them, and add each with an explicit `arcname`
built from the relative path in POSIX form. The archive then looks the same whether it was made on
Windows or Linux, and contains no trace of where `src` lived. The destination is compared with
`resolve()` so the archive does not swallow itself when it is written inside `src`.

**Reading.** `namelist()` returns names in archive order; sorting gives a stable answer.
Folder entries (names ending in `/`) exist in some archives and are skipped.

**Extracting safely.** Validation happens in a first pass over *all* names; only when every name is
safe does `extractall` run. A name is checked by its **parts**: `..` as a whole part climbs a level,
while `..hidden` is a normal name. Backslashes are refused because Windows treats them as separators.

## Code

```python
import zipfile
from pathlib import Path, PurePosixPath


def zip_folder(src, dest_zip):
    src = Path(src)
    dest_zip = Path(dest_zip)
    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in src.rglob("*") if p.is_file() and p.resolve() != dest_zip.resolve())
    names = []
    with zipfile.ZipFile(dest_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            arcname = path.relative_to(src).as_posix()
            zf.write(path, arcname=arcname)
            names.append(arcname)
    return sorted(names)


def list_zip(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        return sorted(name for name in zf.namelist() if not name.endswith("/"))


def read_member(zip_path, name):
    with zipfile.ZipFile(zip_path) as zf:
        return zf.read(name)


def is_safe_name(name):
    if name.startswith(("/", "\\")) or "\\" in name:
        return False
    parts = PurePosixPath(name).parts
    if parts and ":" in parts[0]:
        return False
    return ".." not in parts


def safe_extract(zip_path, dest):
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        for name in names:
            if not is_safe_name(name):
                raise ValueError(f"unsafe member name: {name!r}")
        zf.extractall(dest)
    return sorted(name for name in names if not name.endswith("/"))
```

## Complexity

O(total bytes) to compress or extract, plus O(F log F) for sorting F names.

## Another way

`ZipFile.extractall` itself already removes `..` and drive letters from names (it "sanitises" them),
so it would not write outside `dest`, but it silently writes `evil.txt` somewhere you did not expect.
Refusing the whole archive is clearer. A different check: compute
`(dest / name).resolve()` and require that it is inside `dest.resolve()` (`is_relative_to`), which also
works for symlink tricks in other archive formats.
