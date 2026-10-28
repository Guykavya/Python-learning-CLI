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
        for name in names:                       # check everything before writing anything
            if not is_safe_name(name):
                raise ValueError(f"unsafe member name: {name!r}")
        zf.extractall(dest)
    return sorted(name for name in names if not name.endswith("/"))
