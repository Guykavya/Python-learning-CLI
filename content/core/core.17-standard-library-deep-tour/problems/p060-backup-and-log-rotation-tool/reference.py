import hashlib
import logging
import logging.handlers
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = "MANIFEST.sha256"
STAMP = "%Y%m%d-%H%M%S"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
DEFAULT_LOGGER = "backup_tool"


# ------------------------------------------------------------------ Part 1: names
def backup_name(prefix, when):
    if when.tzinfo is None or when.utcoffset() is None:
        raise ValueError("use an aware datetime (with a time zone)")
    utc = when.astimezone(timezone.utc)
    return f"{prefix}-{utc.strftime(STAMP)}.zip"


def parse_backup_name(prefix, filename):
    start = prefix + "-"
    if not (filename.startswith(start) and filename.endswith(".zip")):
        return None
    stamp = filename[len(start):-len(".zip")]
    if len(stamp) != 15:
        return None
    try:
        naive = datetime.strptime(stamp, STAMP)
    except ValueError:
        return None
    return naive.replace(tzinfo=timezone.utc)


# ------------------------------------------------------------------ Part 2: manifest
def sha256_file(path, chunk_size=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def build_manifest(src):
    src = Path(src)
    files = sorted(p.relative_to(src).as_posix() for p in src.rglob("*") if p.is_file())
    return {name: sha256_file(src / name) for name in files}


def manifest_text(manifest):
    return "".join(f"{manifest[name]}  {name}\n" for name in sorted(manifest))


def parse_manifest(text):
    result = {}
    for line in text.splitlines():
        if line.strip():
            digest, name = line.split("  ", 1)
            result[name] = digest
    return result


# ------------------------------------------------------------------ Part 3: create
def create_backup(src, dest_dir, prefix="backup", clock=None, logger=None):
    src = Path(src)
    dest_dir = Path(dest_dir)
    logger = logger or logging.getLogger(DEFAULT_LOGGER)
    clock = clock or (lambda: datetime.now(timezone.utc))
    if not src.is_dir():
        raise FileNotFoundError(f"source folder {src} does not exist")
    src_abs, dest_abs = src.resolve(), dest_dir.resolve()
    if dest_abs == src_abs or src_abs in dest_abs.parents:
        raise ValueError("the backup folder must not be inside the source folder")

    manifest = build_manifest(src)
    if MANIFEST in manifest:
        raise ValueError(f"the source already contains a file named {MANIFEST}")

    dest_dir.mkdir(parents=True, exist_ok=True)
    final = dest_dir / backup_name(prefix, clock())
    if final.exists():
        raise FileExistsError(final)
    part = final.with_name(final.name + ".part")
    try:
        with zipfile.ZipFile(part, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for name in manifest:                       # already sorted
                zf.write(src / name, arcname=name)
            zf.writestr(MANIFEST, manifest_text(manifest))
        os.replace(part, final)                         # appears complete, or not at all
    except BaseException:
        part.unlink(missing_ok=True)
        raise
    logger.info("created %s (%d files, %d bytes)", final.name, len(manifest), final.stat().st_size)
    return final


# ------------------------------------------------------------------ Part 4: verify
def _member_hash(zf, name):
    h = hashlib.sha256()
    with zf.open(name) as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def verify_backup(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        names = {n for n in zf.namelist() if not n.endswith("/")}
        if MANIFEST not in names:
            return [f"missing: {MANIFEST}"]
        expected = parse_manifest(zf.read(MANIFEST).decode("utf-8"))
        problems = []
        for name, digest in expected.items():
            if name not in names:
                problems.append(f"missing: {name}")
            elif _member_hash(zf, name) != digest:
                problems.append(f"corrupt: {name}")
        for name in names - set(expected) - {MANIFEST}:
            problems.append(f"extra: {name}")
    return sorted(problems)


# ------------------------------------------------------------------ Part 5: rotation
def list_backups(dest_dir, prefix):
    dest_dir = Path(dest_dir)
    if not dest_dir.is_dir():
        return []
    found = []
    for path in dest_dir.iterdir():
        when = parse_backup_name(prefix, path.name)
        if when is not None and path.is_file():
            found.append((when, path))
    found.sort()
    return [path for _, path in found]


def rotate_backups(dest_dir, prefix, keep, logger=None):
    if keep < 1:
        raise ValueError("keep must be at least 1")
    logger = logger or logging.getLogger(DEFAULT_LOGGER)
    backups = list_backups(dest_dir, prefix)
    old = backups[:-keep]
    for path in old:
        path.unlink()
        logger.info("deleted old backup %s", path.name)
    return old


# ------------------------------------------------------------------ Part 6: logging
def close_log(logger):
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()


def setup_log(log_path, max_bytes=1024, backup_count=3, name=DEFAULT_LOGGER):
    logger = logging.getLogger(name)
    close_log(logger)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    return logger


# ------------------------------------------------------------------ Part 7: one run
def run_backup(src, dest_dir, keep, prefix="backup", clock=None, logger=None):
    logger = logger or logging.getLogger(DEFAULT_LOGGER)
    created = create_backup(src, dest_dir, prefix, clock, logger)
    problems = verify_backup(created)
    if problems:
        logger.error("backup %s failed verification: %s", created.name, ", ".join(problems))
        raise RuntimeError(f"backup {created.name} is damaged: {problems}")
    deleted = rotate_backups(dest_dir, prefix, keep, logger)
    with zipfile.ZipFile(created) as zf:
        files = len([n for n in zf.namelist() if n != MANIFEST])
    return {"created": created, "deleted": deleted, "files": files}
