import hashlib
import logging
import logging.handlers
import os
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import solution
from solution import (
    MANIFEST,
    backup_name,
    build_manifest,
    close_log,
    create_backup,
    list_backups,
    manifest_text,
    parse_backup_name,
    parse_manifest,
    rotate_backups,
    run_backup,
    setup_log,
    sha256_file,
    verify_backup,
)

UTC = timezone.utc
IST = timezone(timedelta(hours=5, minutes=30))
T0 = datetime(2025, 1, 15, 9, 30, 0, tzinfo=UTC)

FILES = {
    "notes.txt": b"buy milk\n",
    "docs/report.md": b"# Report\n" + b"line\n" * 200,
    "docs/img/logo.bin": bytes(range(256)),
    "my file.txt": b"spaces in the name\n",
}


class FakeClock:
    """Returns T0, then T0 + step, then T0 + 2*step, ... : no real time is used."""

    def __init__(self, start=T0, step=timedelta(hours=1)):
        self.now = start
        self.step = step
        self.calls = 0

    def __call__(self):
        value = self.now
        self.now += self.step
        self.calls += 1
        return value


@pytest.fixture
def src(tmp_path):
    root = tmp_path / "src"
    for rel, data in FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return root


@pytest.fixture
def log(request, caplog):
    """A unique logger whose records pytest captures; cleaned up afterwards."""
    name = f"p060.{request.node.name}"
    caplog.set_level(logging.INFO, logger=name)
    logger = logging.getLogger(name)
    yield logger
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()


def messages(caplog, logger):
    return [(r.levelname, r.getMessage()) for r in caplog.records if r.name == logger.name]


def sha(data):
    return hashlib.sha256(data).hexdigest()


# =============================================================== Part 1: backup names
def test_backup_name_utc():
    assert backup_name("site", T0) == "site-20250115-093000.zip", "Name = prefix-YYYYMMDD-HHMMSS.zip (strftime('%Y%m%d-%H%M%S'))."


def test_backup_name_converts_to_utc():
    ist = datetime(2025, 1, 15, 15, 0, 0, tzinfo=IST)     # 15:00 in India is 09:30 UTC
    assert backup_name("site", ist) == "site-20250115-093000.zip", (
        "Names always use UTC: convert with when.astimezone(timezone.utc) before formatting."
    )
    late = datetime(2025, 1, 1, 2, 0, 0, tzinfo=IST)       # still 31 December in UTC
    assert backup_name("b", late) == "b-20241231-203000.zip", "Converting to UTC can change the date too."


def test_backup_name_refuses_naive():
    with pytest.raises(ValueError):
        backup_name("site", datetime(2025, 1, 15, 9, 30))


def test_parse_backup_name():
    when = parse_backup_name("site", "site-20250115-093000.zip")
    assert when == T0, "parse_backup_name reads the timestamp back."
    assert when.tzinfo is not None and when.utcoffset() == timedelta(0), "Return an AWARE datetime in UTC (tzinfo=timezone.utc)."
    assert parse_backup_name("site", backup_name("site", T0 + timedelta(seconds=59))) == T0 + timedelta(seconds=59), (
        "backup_name and parse_backup_name must be exact opposites."
    )


@pytest.mark.parametrize(
    "filename",
    [
        "other-20250115-093000.zip",      # another prefix
        "site-20250115-093000.tar",       # another extension
        "site-20251315-093000.zip",       # month 13
        "site-a-20250115-093000.zip",     # belongs to the prefix 'site-a'
        "site-20250115-093000.zip.part",  # unfinished
        "site-2025115-93000.zip",         # wrong length
        "site-.zip",
        "notes.txt",
    ],
)
def test_parse_backup_name_rejects(filename):
    assert parse_backup_name("site", filename) is None, (
        f"{filename!r} is not a backup of prefix 'site': return None (catch strptime's ValueError, check prefix, length and '.zip')."
    )


# =============================================================== Part 2: hashes and manifest
def test_sha256_file(tmp_path):
    path = tmp_path / "x.bin"
    path.write_bytes(b"abc")
    assert sha256_file(path) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", "sha256 hexdigest of the file's bytes."
    assert sha256_file(path, chunk_size=1) == sha(b"abc"), "The chunk size must not change the digest."


def test_build_manifest(src):
    manifest = build_manifest(src)
    assert manifest == {name: sha(data) for name, data in FILES.items()}, (
        "build_manifest maps every file's path relative to src (with '/') to its sha256 hex digest."
    )
    assert list(manifest) == sorted(FILES), "The keys must be in sorted order."


def test_manifest_text_and_parse():
    manifest = {"b.txt": "2" * 64, "a dir/my file.txt": "1" * 64}
    text = manifest_text(manifest)
    assert text == "1" * 64 + "  a dir/my file.txt\n" + "2" * 64 + "  b.txt\n", (
        "One line per file, sorted by name: '<digest>  <name>' (TWO spaces, like the sha256sum tool), each ending in '\\n'."
    )
    assert parse_manifest(text) == manifest, "parse_manifest must undo manifest_text, also for names with spaces (split once)."
    assert parse_manifest("") == {}, "An empty manifest gives an empty dict."


# =============================================================== Part 3: create a backup
def test_create_backup_name_and_place(src, tmp_path, log):
    dest = tmp_path / "backups" / "daily"
    path = create_backup(src, dest, prefix="site", clock=FakeClock(), logger=log)
    assert path == dest / "site-20250115-093000.zip", "The archive goes in dest_dir and is named from the INJECTED clock (not the real time)."
    assert path.is_file(), "The archive must exist (create dest_dir with mkdir(parents=True, exist_ok=True))."
    assert sorted(p.name for p in dest.iterdir()) == [path.name], (
        "Only the finished archive may be left in dest_dir: write to a temporary '.part' file and os.replace it, "
        "and leave nothing else behind."
    )


def test_create_backup_contents(src, tmp_path, log):
    path = create_backup(src, tmp_path / "out", clock=FakeClock(), logger=log)
    with zipfile.ZipFile(path) as zf:
        names = sorted(zf.namelist())
        assert names == sorted([*FILES, MANIFEST]), (
            "Members are the relative posix paths of all files plus MANIFEST.sha256; no folder entries, no absolute paths."
        )
        for rel, data in FILES.items():
            assert zf.read(rel) == data, f"{rel} must be stored byte for byte."
        assert zf.read(MANIFEST).decode("utf-8") == manifest_text(build_manifest(src)), (
            "The MANIFEST.sha256 member holds manifest_text(build_manifest(src))."
        )
        assert zf.getinfo("docs/report.md").compress_type == zipfile.ZIP_DEFLATED, "Use compression=zipfile.ZIP_DEFLATED."


def test_create_backup_default_prefix(src, tmp_path, log):
    path = create_backup(src, tmp_path / "out", clock=FakeClock(), logger=log)
    assert path.name == "backup-20250115-093000.zip", "The default prefix is 'backup'."


def test_create_backup_same_second_refused(src, tmp_path, log):
    dest = tmp_path / "out"
    first = create_backup(src, dest, clock=FakeClock(), logger=log)
    before = first.read_bytes()
    with pytest.raises(FileExistsError):
        create_backup(src, dest, clock=FakeClock(), logger=log)     # same time again
    assert first.read_bytes() == before, "An existing backup must never be overwritten."


def test_create_backup_dest_inside_src_refused(src, log):
    with pytest.raises(ValueError):
        create_backup(src, src / "backups", clock=FakeClock(), logger=log)
    assert not (src / "backups").exists(), "Refuse BEFORE creating anything: a backup folder inside src would back up the backups."


def test_create_backup_missing_src(tmp_path, log):
    with pytest.raises(FileNotFoundError):
        create_backup(tmp_path / "nope", tmp_path / "out", clock=FakeClock(), logger=log)


def test_create_backup_name_clash_with_manifest(src, tmp_path, log):
    (src / MANIFEST).write_text("mine", encoding="utf-8")
    with pytest.raises(ValueError):
        create_backup(src, tmp_path / "out", clock=FakeClock(), logger=log)


def test_create_backup_logs(src, tmp_path, log, caplog):
    path = create_backup(src, tmp_path / "out", clock=FakeClock(), logger=log)
    size = path.stat().st_size
    assert messages(caplog, log) == [("INFO", f"created {path.name} (4 files, {size} bytes)")], (
        "Log one INFO line: 'created %s (%d files, %d bytes)' with the archive name, the number of files, and the archive size."
    )


# =============================================================== Part 4: verify
def rebuild(path, changes):
    """Copy the archive, replacing members (bytes) or deleting them (None)."""
    with zipfile.ZipFile(path) as zf:
        members = {n: zf.read(n) for n in zf.namelist()}
    for name, data in changes.items():
        if data is None:
            members.pop(name, None)
        else:
            members[name] = data
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)


def test_verify_fresh_backup(src, tmp_path, log):
    path = create_backup(src, tmp_path / "out", clock=FakeClock(), logger=log)
    assert verify_backup(path) == [], "A fresh backup matches its manifest: no problems."


def test_verify_detects_corruption(src, tmp_path, log):
    path = create_backup(src, tmp_path / "out", clock=FakeClock(), logger=log)
    rebuild(path, {"notes.txt": b"buy MILK\n"})
    assert verify_backup(path) == ["corrupt: notes.txt"], "Recompute the sha256 of each member and compare it with the manifest."


def test_verify_missing_and_extra(src, tmp_path, log):
    path = create_backup(src, tmp_path / "out", clock=FakeClock(), logger=log)
    rebuild(path, {"my file.txt": None, "sneaky.exe": b"MZ"})
    assert verify_backup(path) == ["extra: sneaky.exe", "missing: my file.txt"], (
        "Report 'missing: name' for manifest entries not in the zip and 'extra: name' for members not in the manifest; sorted."
    )


def test_verify_without_manifest(tmp_path):
    path = tmp_path / "plain.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("a.txt", "a")
    assert verify_backup(path) == [f"missing: {MANIFEST}"], "Without a manifest nothing can be checked: report it missing."


# =============================================================== Part 5: listing and rotation
def make_backups(dest, prefix, times):
    dest.mkdir(parents=True, exist_ok=True)
    paths = []
    for when in times:
        path = dest / backup_name(prefix, when)
        path.write_bytes(b"PK")
        paths.append(path)
    return paths


def test_list_backups_by_name_time_not_mtime(tmp_path):
    dest = tmp_path / "b"
    times = [T0 + timedelta(days=d) for d in (3, 0, 10, 1)]
    paths = make_backups(dest, "site", times)
    for i, path in enumerate(paths):              # give them misleading modification times
        os.utime(path, (1_000_000 + i, 1_000_000 - i * 1000))
    (dest / "readme.txt").write_text("not a backup", encoding="utf-8")
    (dest / "other-20250101-000000.zip").write_bytes(b"PK")
    (dest / "site-20250301-000000.zip.part").write_bytes(b"PK")
    names = [p.name for p in list_backups(dest, "site")]
    assert names == [
        "site-20250115-093000.zip",
        "site-20250116-093000.zip",
        "site-20250118-093000.zip",
        "site-20250125-093000.zip",
    ], "Oldest first, ordered by the time IN THE NAME (file times change when files are copied); ignore files of other prefixes."


def test_list_backups_missing_folder(tmp_path):
    assert list_backups(tmp_path / "nothing-here", "site") == [], "A folder that does not exist yet has no backups."


def test_rotate_keeps_newest(tmp_path, log, caplog):
    dest = tmp_path / "b"
    paths = make_backups(dest, "site", [T0 + timedelta(hours=h) for h in range(5)])
    deleted = rotate_backups(dest, "site", keep=2, logger=log)
    assert deleted == paths[:3], "rotate_backups returns the deleted paths, oldest first."
    assert sorted(p.name for p in dest.iterdir()) == [p.name for p in paths[3:]], "Only the 2 newest backups remain."
    assert messages(caplog, log) == [("INFO", f"deleted old backup {p.name}") for p in paths[:3]], (
        "Log 'deleted old backup %s' (INFO) for each file removed."
    )


def test_rotate_leaves_other_files(tmp_path, log):
    dest = tmp_path / "b"
    make_backups(dest, "site", [T0, T0 + timedelta(hours=1)])
    other = make_backups(dest, "db", [T0 - timedelta(days=30)])[0]
    rotate_backups(dest, "site", keep=1, logger=log)
    assert other.exists(), "Backups of another prefix are never touched."


def test_rotate_nothing_to_do(tmp_path, log):
    dest = tmp_path / "b"
    paths = make_backups(dest, "site", [T0, T0 + timedelta(hours=1)])
    assert rotate_backups(dest, "site", keep=5, logger=log) == [], "Fewer backups than keep: delete nothing."
    assert all(p.exists() for p in paths), "All backups must still be there."


def test_rotate_keep_must_be_positive(tmp_path, log):
    dest = tmp_path / "b"
    paths = make_backups(dest, "site", [T0])
    with pytest.raises(ValueError):
        rotate_backups(dest, "site", keep=0, logger=log)
    assert paths[0].exists(), "keep=0 would delete every backup: refuse it (and note backups[:-0] is an empty slice!)."


# =============================================================== Part 6: the rotating log
@pytest.fixture
def logname(request):
    name = f"p060.log.{request.node.name}"
    yield name
    logger = logging.getLogger(name)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    logger.propagate = True
    logger.setLevel(logging.NOTSET)


def test_setup_log(tmp_path, logname):
    path = tmp_path / "tool.log"
    setup_log(path, name=logname)
    logger = setup_log(path, name=logname)               # twice on purpose
    assert logger.name == logname and logger.level == logging.INFO, "setup_log returns the named logger at level INFO."
    assert len(logger.handlers) == 1, "Calling setup_log twice must still leave ONE handler: remove (and close) old ones first."
    handler = logger.handlers[0]
    assert isinstance(handler, logging.handlers.RotatingFileHandler), "Use logging.handlers.RotatingFileHandler."
    assert logger.propagate is False, "The tool's log goes only to its file: propagate = False."
    logger.info("hello %s", "world")
    logger.debug("hidden")
    close_log(logger)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1 and lines[0].endswith(" INFO hello world"), "Format '%(asctime)s %(levelname)s %(message)s'; DEBUG is below INFO."
    datetime.strptime(lines[0][:19], "%Y-%m-%d %H:%M:%S")   # asctime starts with the date and time


def test_log_rotation(tmp_path, logname):
    path = tmp_path / "tool.log"
    logger = setup_log(path, max_bytes=200, backup_count=2, name=logname)
    for i in range(40):
        logger.info("message number %02d", i)
    close_log(logger)
    names = sorted(p.name for p in tmp_path.iterdir())
    assert names == ["tool.log", "tool.log.1", "tool.log.2"], (
        "With backup_count=2 only tool.log, tool.log.1 and tool.log.2 may exist: pass maxBytes and backupCount to RotatingFileHandler."
    )
    for name in names:
        assert (tmp_path / name).stat().st_size <= 200, f"{name} is bigger than max_bytes: the handler should have rolled over."
    newest = (tmp_path / "tool.log").read_text(encoding="utf-8").splitlines()
    assert newest[-1].endswith("message number 39"), "The newest messages are in tool.log itself."
    older = (tmp_path / "tool.log.1").read_text(encoding="utf-8").splitlines()
    assert int(older[-1][-2:]) < int(newest[0][-2:]), "tool.log.1 holds OLDER messages than tool.log."


def test_close_log(tmp_path, logname):
    path = tmp_path / "c.log"
    logger = setup_log(path, name=logname)
    handler = logger.handlers[0]
    close_log(logger)
    assert logger.handlers == [] and handler.stream is None, "close_log removes AND closes every handler."
    path.unlink()                                          # only possible on Windows when closed


# =============================================================== Part 7: a full run
def test_run_backup_end_to_end(src, tmp_path, log):
    dest = tmp_path / "backups"
    clock = FakeClock(step=timedelta(days=1))
    results = [run_backup(src, dest, keep=2, prefix="site", clock=clock, logger=log) for _ in range(4)]
    assert clock.calls == 4, "Each run asks the injected clock for the time exactly once."
    last = results[-1]
    assert last["created"] == dest / "site-20250118-093000.zip", "The 4th run (T0 + 3 days) creates site-20250118-093000.zip."
    assert last["files"] == 4, "'files' counts the backed-up files (not the manifest)."
    assert [p.name for p in last["deleted"]] == ["site-20250116-093000.zip"], "The 4th run deletes the one backup that is now 3rd newest."
    assert [p.name for p in list_backups(dest, "site")] == ["site-20250117-093000.zip", "site-20250118-093000.zip"], (
        "After four runs with keep=2 only the two newest backups remain."
    )
    assert results[0]["deleted"] == [] and results[1]["deleted"] == [], "The first two runs delete nothing."
    assert verify_backup(last["created"]) == [], "The newest backup must verify cleanly."


def test_run_backup_never_rotates_after_bad_backup(src, tmp_path, log, caplog, monkeypatch):
    dest = tmp_path / "backups"
    clock = FakeClock(step=timedelta(days=1))
    run_backup(src, dest, keep=1, clock=clock, logger=log)
    monkeypatch.setattr(solution, "verify_backup", lambda path: ["corrupt: notes.txt"])
    with pytest.raises(RuntimeError):
        run_backup(src, dest, keep=1, clock=clock, logger=log)
    assert len(list_backups(dest, "backup")) == 2, (
        "If the new backup fails verify_backup, raise RuntimeError BEFORE rotating: never delete good old backups "
        "because of a bad new one. Call verify_backup by that name so this test can replace it."
    )
    assert any(level == "ERROR" and "corrupt: notes.txt" in text for level, text in messages(caplog, log)), (
        "Log an ERROR naming the problems before raising."
    )


def test_run_backup_writes_rotating_log(src, tmp_path, logname):
    log_path = tmp_path / "logs" / "tool.log"
    log_path.parent.mkdir()
    logger = setup_log(log_path, max_bytes=10_000, backup_count=1, name=logname)
    try:
        clock = FakeClock()
        run_backup(src, tmp_path / "backups", keep=1, clock=clock, logger=logger)
        run_backup(src, tmp_path / "backups", keep=1, clock=clock, logger=logger)
    finally:
        close_log(logger)
    text = log_path.read_text(encoding="utf-8")
    assert "INFO created backup-20250115-093000.zip (4 files," in text, "The 'created' line must reach the rotating log file."
    assert "INFO deleted old backup backup-20250115-093000.zip" in text, "The second run deletes the first backup and logs it."
