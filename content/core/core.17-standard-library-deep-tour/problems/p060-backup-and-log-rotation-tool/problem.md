# Project: a backup and log-rotation tool

This is the **build** assessment of the module. You will write a small but real backup tool, using
many of the modules from this chapter together: `zipfile`, `hashlib`, `datetime`, `pathlib`, `os`
and `logging` (with `logging.handlers.RotatingFileHandler`). Everything goes into `solution.py`.

What the tool does, in one run:

1. zip a folder into `dest_dir/<prefix>-YYYYMMDD-HHMMSS.zip` (time in **UTC**), with a SHA-256
   **manifest** inside the archive;
2. check the new archive against its manifest;
3. delete old backups so only the `keep` newest remain;
4. record all of it in a log file that **rotates** (never grows without limit).

**The clock is injected.** Functions that need "now" take `clock`, a function with no arguments that
returns an **aware** `datetime`. In real use it is `lambda: datetime.now(timezone.utc)` (the default
when `clock` is `None`); the tests pass a fake clock, so no test depends on the real time or sleeps.

**The logger is injected too.** Functions that log take `logger`; when it is `None`, use
`logging.getLogger("backup_tool")`.

## Part 1: names

| Function | Behaviour |
|---|---|
| `backup_name(prefix, when) -> str` | `f"{prefix}-YYYYMMDD-HHMMSS.zip"` with `when` converted to UTC first. A naive `when` (no time zone) raises `ValueError`. |
| `parse_backup_name(prefix, filename) -> datetime \| None` | The aware UTC datetime in a name made by `backup_name`, or `None` for anything else (another prefix, not `.zip`, an impossible date, wrong length, a `.part` file, ...). |

## Part 2: hashes and the manifest

| Function | Behaviour |
|---|---|
| `sha256_file(path, chunk_size=65536) -> str` | Hex digest, read in chunks. |
| `build_manifest(src) -> dict[str, str]` | Every file under `src` (all levels): relative path with `/` mapped to its digest. Keys in sorted order. |
| `manifest_text(manifest) -> str` | One line per file, sorted by name: `"<digest>  <name>\n"` (two spaces, the format of the `sha256sum` tool). |
| `parse_manifest(text) -> dict[str, str]` | The reverse. Names may contain spaces. |

## Part 3: create a backup

`create_backup(src, dest_dir, prefix="backup", clock=None, logger=None) -> Path`

- `src` must be an existing folder, else `FileNotFoundError`.
- `dest_dir` must not be `src` or inside it, else `ValueError` (check before creating anything).
- If `src` contains a file named `MANIFEST.sha256` at the top, raise `ValueError` (it would clash).
- Create `dest_dir` if needed. The archive is `dest_dir / backup_name(prefix, clock())`. If that file
  already exists, raise `FileExistsError` (never overwrite a backup).
- Write a `ZIP_DEFLATED` archive with every file under its relative posix path, plus a member
  `MANIFEST.sha256` holding `manifest_text(build_manifest(src))`.
- Write it first as `<name>.zip.part` and rename it with `os.replace` when complete, so a crash never
  leaves a half-written file with a real backup name. Remove the `.part` file if anything fails.
- Log `INFO` `"created %s (%d files, %d bytes)"`: archive name, number of files, archive size.

## Part 4: verify

`verify_backup(zip_path) -> list[str]`: re-hash every member and compare it with the manifest inside
the archive. Return a **sorted** list of problems: `"missing: <name>"` (in the manifest, not in the
zip), `"corrupt: <name>"` (digest differs), `"extra: <name>"` (in the zip, not in the manifest). No
manifest at all: `["missing: MANIFEST.sha256"]`. An empty list means the backup is good.

## Part 5: listing and rotation

| Function | Behaviour |
|---|---|
| `list_backups(dest_dir, prefix) -> list[Path]` | The backups of that prefix, **oldest first, by the time in the name** (file modification times change when files are copied, so do not use them). Other files are ignored. A missing folder gives `[]`. |
| `rotate_backups(dest_dir, prefix, keep, logger=None) -> list[Path]` | Delete all but the `keep` newest; return the deleted paths, oldest first. Log `INFO` `"deleted old backup %s"` (file name) for each. `keep < 1` raises `ValueError`. |

## Part 6: the rotating log

| Function | Behaviour |
|---|---|
| `setup_log(log_path, max_bytes=1024, backup_count=3, name="backup_tool") -> Logger` | The logger `name` at level `INFO`, `propagate = False`, with **one** `RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")` and the format `"%(asctime)s %(levelname)s %(message)s"`. Calling it again replaces (and closes) the old handler. |
| `close_log(logger)` | Remove and close every handler. |

When the file would grow past `max_bytes`, the handler renames `tool.log` to `tool.log.1` (and
`.1` to `.2`, ...), keeps at most `backup_count` old files, and starts a fresh `tool.log`.

## Part 7: one complete run

`run_backup(src, dest_dir, keep, prefix="backup", clock=None, logger=None) -> dict`

1. `create_backup(...)`;
2. `verify_backup(created)` (call it by this name). If it reports problems: log an `ERROR` that
   includes the problems, and raise `RuntimeError` **without rotating** (a bad new backup must never
   cause good old ones to be deleted);
3. `rotate_backups(dest_dir, prefix, keep, logger)`;
4. return `{"created": <Path>, "deleted": [<Path>, ...], "files": <number of files backed up>}`.

## Example

```python
from datetime import datetime, timedelta, timezone

times = iter([datetime(2025, 1, 15, 9, 30, tzinfo=timezone.utc) + timedelta(days=d) for d in range(4)])
clock = lambda: next(times)

log = setup_log("logs/tool.log", max_bytes=5000, backup_count=2)
try:
    for _ in range(4):
        result = run_backup("my_project", "backups", keep=2, prefix="site", clock=clock, logger=log)
finally:
    close_log(log)

result["created"].name                       # 'site-20250118-093000.zip'
[p.name for p in result["deleted"]]          # ['site-20250116-093000.zip']
[p.name for p in list_backups("backups", "site")]
# ['site-20250117-093000.zip', 'site-20250118-093000.zip']
backup_name("b", datetime(2025, 1, 1, 2, 0, tzinfo=timezone(timedelta(hours=5, minutes=30))))
# 'b-20241231-203000.zip'          02:00 in India is still 31 December in UTC
```

`logs/tool.log` then contains lines like these (times and sizes depend on your run):

```text
2025-06-02 18:04:11,532 INFO created site-20250115-093000.zip (4 files, 1830 bytes)
...
2025-06-02 18:04:11,561 INFO deleted old backup site-20250116-093000.zip
```

## Advice

Work in the order of the parts; the test file follows the same order, and each part uses the earlier
ones. Run the tests after each part. Every helper you write once (`sha256_file`, `backup_name`,
`parse_backup_name`) is used again later: do not write the same logic twice.

## Ideas to go further (not tested)

A command-line interface with `argparse` (`backup.py SRC DEST --keep 7 -v`); `restore(zip, dest)`
that verifies first and extracts safely; keep "one per day for a week, one per week for a month";
excluding patterns such as `__pycache__` with `fnmatch`; a `TimedRotatingFileHandler` that starts a new
log every midnight.
