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
