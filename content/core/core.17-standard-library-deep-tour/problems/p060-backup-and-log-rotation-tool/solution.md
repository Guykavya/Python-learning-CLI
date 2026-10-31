## Approach

The tool is a stack of small functions; each one is easy to test alone and the last one only
combines them.

**Time.** "Now" comes from an injected `clock`. Names always use UTC, so they sort correctly as
plain text and as times, mean the same on every machine, and are not disturbed by daylight saving.
`parse_backup_name` is the exact inverse of `backup_name` and is the *only* place that decides
whether a file is a backup; listing and rotation reuse it.

**Integrity.** The manifest records a SHA-256 for every file at backup time, inside the archive
itself, in the standard `sha256sum` format (so `sha256sum -c MANIFEST.sha256` works on an extracted
copy). `verify_backup` re-hashes each member from the archive and compares. It reports missing,
corrupt and extra members separately because each one means something different.

**Safety.** The archive is written under a temporary `.part` name and renamed with `os.replace`,
which is atomic on the same file system: a backup with a real name is always complete. Existing
backups are never overwritten. Rotation runs only after the new backup verified, and refuses
`keep < 1`.

**Logging.** The functions receive a logger and only emit messages. `setup_log` is the one place
that configures output: a `RotatingFileHandler` caps each file at `max_bytes` and keeps
`backup_count` old files, so the log can never fill the disk.

## Code

```python
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
            for name in manifest:
                zf.write(src / name, arcname=name)
            zf.writestr(MANIFEST, manifest_text(manifest))
        os.replace(part, final)
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
```

## Complexity

A run reads every byte of `src` twice (once to hash, once to compress) and every byte of the archive
once more to verify: O(total size). Listing and rotation are O(B log B) for B files in `dest_dir`.
Memory stays at one chunk per file, whatever the file sizes.

## Another way

- Hash while compressing: open each source file once, feed chunks both to a hash object and to
  `zf.open(name, "w")`, which halves the reading of `src`.
- Sorting by name alone works too, because `YYYYMMDD-HHMMSS` in UTC sorts the same way as the time;
  parsing is still needed to ignore files that only *look* like backups.
- For time-based log rotation, `logging.handlers.TimedRotatingFileHandler(path, when="midnight",
  backupCount=7)` starts a new file every day instead of by size.
- Real tools (restic, borg) split files into chunks and store each unique chunk once
  (deduplication): seven daily backups of a mostly unchanged folder then cost little more than one.
