import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import pytest

import solution
from solution import FakeTransport, main

NOW = datetime(2026, 11, 21, 8, 0, tzinfo=timezone.utc)
EXPORT = "region,amount\nnorth,1200.50\nsouth,830\nnorth,99.50\neast,abc\nwest,410.25\n"


@pytest.fixture(autouse=True)
def close_log_handlers():
    yield
    log = logging.getLogger("auto")
    for h in list(log.handlers):
        log.removeHandler(h)
        h.close()


def snapshot(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None) for p in sorted(root.rglob("*"))}


def status(status_dir, name):
    return json.loads((status_dir / f"{name}.json").read_text(encoding="utf-8"))


@pytest.fixture
def env():
    return {}


@pytest.fixture
def status_dir(tmp_path):
    return tmp_path / "status"


@pytest.fixture
def messy(tmp_path):
    folder = tmp_path / "downloads"
    folder.mkdir()
    for name, data in {"a.pdf": b"pdf", "b.PNG": b"png", "README": b"none", ".hidden": b"h"}.items():
        (folder / name).write_bytes(data)
    return folder


def auto(status_dir, *argv, **kwargs):
    kwargs.setdefault("env", {})
    return main(["--status-dir", str(status_dir), *argv], **kwargs)


# ------------------------------------------------------------------ the command line
def test_help_lists_the_tasks(capsys):
    with pytest.raises(SystemExit) as e:
        main(["--help"], env={})
    assert e.value.code == 0
    out = capsys.readouterr().out
    for name in ("tidy", "report", "cleanup"):
        assert name in out, f"--help must list the task {name!r}."


def test_usage_error_is_2():
    with pytest.raises(SystemExit) as e:
        main(["tidy"], env={})
    assert e.value.code == 2, "A missing argument is a usage error: argparse exits with 2."


# ------------------------------------------------------------------ tidy
def test_tidy_dry_run_changes_nothing(messy, status_dir, capsys):
    before = snapshot(messy)
    assert auto(status_dir, "tidy", str(messy), "--dry-run") == 0
    assert snapshot(messy) == before, "tidy --dry-run must not touch the folder."
    assert "would move: a.pdf -> documents/a.pdf" in capsys.readouterr().out
    s = status(status_dir, "tidy")
    assert s["ok"] is True and s["result"] == {"moved": 3, "dry_run": True}, f"Status file of the run; got {s}"


def test_tidy_and_undo(messy, status_dir, capsys):
    before = snapshot(messy)
    assert auto(status_dir, "tidy", str(messy)) == 0
    assert (messy / "documents" / "a.pdf").read_bytes() == b"pdf" and (messy / ".hidden").exists()
    assert auto(status_dir, "tidy", str(messy)) == 0
    assert status(status_dir, "tidy")["result"]["moved"] == 0, "A second tidy finds nothing to move."
    assert auto(status_dir, "tidy", str(messy), "--undo") == 0
    assert snapshot(messy) == before, "tidy --undo restores the folder exactly."
    assert "restored 3 file(s)" in capsys.readouterr().out


def test_tidy_missing_folder_fails(tmp_path, status_dir):
    assert auto(status_dir, "tidy", str(tmp_path / "nope")) == 1, "A task that raises gives exit code 1..."
    s = status(status_dir, "tidy")
    assert s["ok"] is False and "nope" in s["error"], "...and leaves a 'failed' status file naming the problem."


# ------------------------------------------------------------------ report
@pytest.fixture
def export(tmp_path):
    p = tmp_path / "sales.csv"
    p.write_text(EXPORT, encoding="utf-8")
    return p


@pytest.fixture
def config(tmp_path):
    def write(text):
        p = tmp_path / "auto.toml"
        p.write_text(text, encoding="utf-8")
        return p
    return write


def test_report_sends_through_the_transport(export, status_dir, config):
    transport = FakeTransport()
    cfg = config('to = "boss@example.com"\nsender = "reports@example.com"\n')
    assert auto(status_dir, "--config", str(cfg), "report", str(export), transport=transport) == 0
    assert len(transport.sent) == 1, "Exactly one e-mail through the transport you were given."
    msg = transport.sent[0]
    assert msg["To"] == "boss@example.com" and msg["From"] == "reports@example.com", "Recipient and sender come from the settings."
    assert msg["Subject"] == "Weekly sales: 2,540.25"
    assert "could not read line(s) [5]" in msg.get_content(), "Bad rows are reported in the e-mail."
    assert status(status_dir, "report")["ok"] is True


def test_report_dry_run_sends_nothing(export, status_dir, capsys):
    transport = FakeTransport()
    assert auto(status_dir, "report", str(export), "--to", "me@example.com", "--dry-run", transport=transport) == 0
    assert transport.sent == [], "A dry run prints the e-mail and sends nothing."
    assert "Weekly sales: 2,540.25" in capsys.readouterr().out


def test_report_without_transport_fails(export, status_dir):
    assert auto(status_dir, "report", str(export), "--to", "me@example.com") == 1, \
        "No transport and not a dry run: the task must fail (exit 1), never pretend it sent."
    s = status(status_dir, "report")
    assert s["ok"] is False and "transport" in s["error"]


def test_report_recipient_precedence(export, status_dir, config):
    cfg = config('to = "file@example.com"\n')
    t1 = FakeTransport()
    auto(status_dir, "--config", str(cfg), "report", str(export), transport=t1, env={"AUTO_TO": "env@example.com"})
    assert t1.sent[0]["To"] == "env@example.com", "AUTO_TO (environment) beats the config file."
    t2 = FakeTransport()
    auto(status_dir, "--config", str(cfg), "report", str(export), "--to", "flag@example.com",
         transport=t2, env={"AUTO_TO": "env@example.com"})
    assert t2.sent[0]["To"] == "flag@example.com", "--to (flag) beats the environment."


def test_report_without_recipient_fails(export, status_dir):
    assert auto(status_dir, "report", str(export), transport=FakeTransport()) == 1, "No 'to' anywhere: fail loudly."


# ------------------------------------------------------------------ cleanup
@pytest.fixture
def cache(tmp_path):
    folder = tmp_path / "cache"
    folder.mkdir()
    for name, days in {"old.log": 40, "mid.log": 20, "new.log": 1}.items():
        p = folder / name
        p.write_text("x", encoding="utf-8")
        t = (NOW - timedelta(days=days)).timestamp()
        os.utime(p, (t, t))
    return folder


def test_cleanup_is_a_dry_run_by_default(cache, status_dir, capsys):
    before = snapshot(cache)
    assert auto(status_dir, "cleanup", str(cache), now=NOW) == 0
    assert snapshot(cache) == before, "cleanup without --yes deletes nothing."
    assert capsys.readouterr().out.splitlines() == ["would delete: old.log"], "Default keep_days is 30: only old.log is older."


def test_cleanup_yes_uses_settings_precedence(cache, status_dir, config):
    cfg = config("keep_days = 10\n")
    assert auto(status_dir, "--config", str(cfg), "cleanup", str(cache), "--yes", now=NOW, env={"AUTO_KEEP_DAYS": "30"}) == 0
    assert not (cache / "old.log").exists() and (cache / "mid.log").exists(), "AUTO_KEEP_DAYS=30 beats keep_days=10 in the file."
    assert auto(status_dir, "--config", str(cfg), "cleanup", str(cache), "--yes", "--days", "5", now=NOW,
                env={"AUTO_KEEP_DAYS": "30"}) == 0
    assert not (cache / "mid.log").exists() and (cache / "new.log").exists(), "--days 5 beats the environment."
    assert status(status_dir, "cleanup")["ok"] is True


def test_cleanup_of_a_missing_folder_fails(tmp_path, status_dir):
    assert auto(status_dir, "cleanup", str(tmp_path / "nope"), "--yes", now=NOW) == 1


# ------------------------------------------------------------------ shared machinery
def test_second_instance_exits_3(messy, status_dir, capsys):
    status_dir.mkdir()
    lock = status_dir / "auto.lock"
    lock.write_text(str(os.getpid()), encoding="utf-8")            # a live process holds the lock
    before = snapshot(messy)
    assert auto(status_dir, "tidy", str(messy)) == 3, "Another run holds <status_dir>/auto.lock: exit code 3."
    assert snapshot(messy) == before, "The refused run must not do any work."
    assert lock.read_text(encoding="utf-8") == str(os.getpid()), "...and must not remove the other run's lock."
    assert not (status_dir / "tidy.json").exists(), "A refused run records no status."
    assert "already running" in capsys.readouterr().err


def test_lock_is_released(messy, status_dir):
    auto(status_dir, "tidy", str(messy), "--dry-run")
    assert not (status_dir / "auto.lock").exists(), "Release the lock after the task, also when it fails."
    auto(status_dir, "tidy", str(messy / "nope"))
    assert not (status_dir / "auto.lock").exists()


def test_status_dir_from_the_config(messy, tmp_path, config):
    cfg = config(f'status_dir = "{(tmp_path / "from-file").as_posix()}"\n')
    assert main(["--config", str(cfg), "tidy", str(messy), "-n"], env={}) == 0
    assert (tmp_path / "from-file" / "tidy.json").exists(), "status_dir comes from the settings when --status-dir is not given."


def test_unknown_setting_is_reported(messy, status_dir, config, capsys):
    cfg = config("kep_days = 7\n")
    assert auto(status_dir, "--config", str(cfg), "tidy", str(messy), "-n") == 0
    assert "kep_days" in capsys.readouterr().err, "Warn (on stderr, through logging) about unknown keys in the config file."


def test_log_file_gets_the_story(messy, status_dir, tmp_path, config):
    logfile = tmp_path / "auto.log"
    cfg = config(f'log_file = "{logfile.as_posix()}"\n')
    auto(status_dir, "--config", str(cfg), "tidy", str(messy / "nope"))
    text = logfile.read_text(encoding="utf-8")
    assert "tidy" in text and "ERROR" in text, "With log_file set, the log file records the run and its failure (DEBUG and up)."


def test_as_a_real_program(messy, status_dir):
    r = subprocess.run([sys.executable, solution.__file__, "--status-dir", str(status_dir), "tidy", str(messy), "--dry-run"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"The real program must exit 0. stderr: {r.stderr}"
    assert "would move: a.pdf -> documents/a.pdf" in r.stdout
    r = subprocess.run([sys.executable, solution.__file__, "--status-dir", str(status_dir), "tidy", str(messy / "nope")],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 1, "A failing task is exit code 1 for the real program (keep sys.exit(main()))."
