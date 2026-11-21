"""auto: a personal automation suite with three tasks (tidy, report, cleanup)."""
import argparse
import csv
import io
import json
import logging
import logging.handlers
import os
import shutil
import sys
import tempfile
import tomllib
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

log = logging.getLogger("auto")

# ============================================================================ given: small pieces from earlier problems

CATEGORIES = {
    ".jpg": "images", ".jpeg": "images", ".png": "images", ".gif": "images",
    ".pdf": "documents", ".docx": "documents", ".txt": "documents",
    ".csv": "data", ".xlsx": "data", ".json": "data",
    ".zip": "archives", ".tar": "archives", ".gz": "archives",
    ".mp3": "audio", ".wav": "audio",
}
JOURNAL = ".tidy-journal.json"


def category_for(path):
    return CATEGORIES.get(Path(path).suffix.lower(), "other")


def unique_destination(dst):
    """Never overwrite: if 'a.txt' exists, use 'a (1).txt', 'a (2).txt'..."""
    if not dst.exists():
        return dst
    n = 1
    while True:
        candidate = dst.with_name(f"{dst.stem} ({n}){dst.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def write_json_atomic(path, data):
    """Write JSON so a reader sees the old file or the new one, never half (chapter 13.1)."""
    fd, tmp = tempfile.mkstemp(dir=Path(path).parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


class FakeTransport:
    """Stands in for smtplib: records messages instead of sending them."""

    def __init__(self):
        self.sent = []

    def send_message(self, msg):
        self.sent.append(msg)


class AlreadyRunning(Exception):
    pass


def pid_alive(pid):
    """True if a process with this id exists (Linux, macOS and Windows)."""
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            ok = kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
            return bool(ok) and code.value == 259
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


# ============================================================================ settings and logging (p018, p020)

DEFAULTS = {"status_dir": "auto-status", "keep_days": 30, "sender": "auto@localhost", "to": "", "log_file": ""}
ENV_PREFIX = "AUTO_"


def load_settings(config=None, env=None, flags=None):
    """defaults < TOML file < AUTO_* environment < flags (None = not given). Unknown file keys are logged."""
    env = os.environ if env is None else env
    settings = dict(DEFAULTS)
    if config:
        path = Path(config)
        if not path.exists():
            raise FileNotFoundError(f"config file {config} does not exist")
        for key, value in tomllib.loads(path.read_text(encoding="utf-8")).items():
            if key in DEFAULTS:
                settings[key] = value
            else:
                log.warning("unknown setting %r in %s (ignored)", key, config)
    for key in DEFAULTS:
        value = env.get(ENV_PREFIX + key.upper(), "")
        if value != "":
            settings[key] = value
    for key, value in (flags or {}).items():
        if value is not None:
            settings[key] = value
    settings["keep_days"] = int(settings["keep_days"])
    return settings


def setup_logging(verbose=0, logfile=None):
    log.setLevel(logging.DEBUG)
    log.propagate = False
    for handler in list(log.handlers):
        log.removeHandler(handler)
        handler.close()
    console = logging.StreamHandler(sys.stderr)
    console.setLevel([logging.WARNING, logging.INFO, logging.DEBUG][min(verbose, 2)])
    console.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    log.addHandler(console)
    if logfile:
        fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        log.addHandler(fh)


# ============================================================================ lock and runner (p026, p027)

@contextmanager
def single_instance(lock_path, is_alive=None):
    is_alive = is_alive or pid_alive
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        fd = os.open(lock_path, flags)
    except FileExistsError:
        try:
            pid = int(Path(lock_path).read_text(encoding="utf-8").strip())
        except ValueError:
            pid = None
        if pid is not None and is_alive(pid):
            raise AlreadyRunning(f"already running as process {pid}")
        os.unlink(lock_path)
        fd = os.open(lock_path, flags)
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        try:
            os.unlink(lock_path)
        except FileNotFoundError:
            pass


def run_job(name, fn, status_dir, clock):
    Path(status_dir).mkdir(parents=True, exist_ok=True)
    status = {"job": name, "start": clock().isoformat()}
    log.info("job %s starting", name)
    try:
        status.update(ok=True, result=fn(), error=None)
        code = 0
    except Exception as e:
        log.error("job %s failed: %s", name, e)
        status.update(ok=False, result=None, error=f"{type(e).__name__}: {e}")
        code = 1
    status["end"] = clock().isoformat()
    write_json_atomic(Path(status_dir) / f"{name}.json", status)
    log.info("job %s finished: ok=%s", name, status["ok"])
    return code


# ============================================================================ task 1: tidy (p006, p007)

def plan_moves(root):
    moves = []
    for src in sorted(Path(root).iterdir()):
        if src.is_file() and not src.name.startswith("."):
            moves.append((src, unique_destination(Path(root) / category_for(src) / src.name)))
    return moves


def apply_moves(moves, root, dry_run=False):
    done = []
    for src, dst in moves:
        if not dry_run:
            dst.parent.mkdir(exist_ok=True)
            shutil.move(str(src), str(dst))
        done.append((src, dst))
    if done and not dry_run:
        (Path(root) / JOURNAL).write_text(json.dumps([[str(s), str(d)] for s, d in done]), encoding="utf-8")
    return done


def undo(root):
    journal = Path(root) / JOURNAL
    if not journal.exists():
        return []
    restored = []
    for s, d in reversed(json.loads(journal.read_text(encoding="utf-8"))):
        s, d = Path(s), Path(d)
        if d.exists() and not s.exists():
            shutil.move(str(d), str(s))
            restored.append((d, s))
            try:
                d.parent.rmdir()
            except OSError:
                pass
    journal.unlink()
    return restored


def tidy_task(folder, dry_run=False, do_undo=False):
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"{folder} is not a folder")
    if do_undo:
        restored = undo(folder)
        print(f"restored {len(restored)} file(s)")
        return {"restored": len(restored)}
    moves = apply_moves(plan_moves(folder), folder, dry_run)
    label = "would move" if dry_run else "moved"
    for src, dst in moves:
        print(f"{label}: {src.name} -> {dst.relative_to(folder).as_posix()}")
    return {"moved": len(moves), "dry_run": dry_run}


# ============================================================================ task 2: report (p021)

def summarize(csv_text):
    totals, bad = defaultdict(float), []
    for line_no, row in enumerate(csv.DictReader(io.StringIO(csv_text)), start=2):
        try:
            region = row["region"].strip()
            if not region:
                raise ValueError("missing region")
            amount = float(row["amount"])
            totals[region] += amount
        except (KeyError, ValueError, TypeError, AttributeError):
            bad.append(line_no)
    return dict(sorted(totals.items())), bad


def build_email(totals, bad_lines, sender, to):
    grand = sum(totals.values())
    lines = [f"{region:10} {amount:10,.2f}" for region, amount in totals.items()]
    lines.append(f"{'TOTAL':10} {grand:10,.2f}")
    if bad_lines:
        lines.append(f"\nWarning: could not read line(s) {bad_lines}. Please check the export.")
    msg = EmailMessage()
    msg["Subject"] = f"Weekly sales: {grand:,.2f}"
    msg["From"], msg["To"] = sender, to
    msg.set_content("\n".join(lines))
    return msg


def report_task(csv_file, sender, to, transport, dry_run=False):
    totals, bad = summarize(Path(csv_file).read_text(encoding="utf-8"))
    if not to:
        raise ValueError("no recipient: set 'to' in the config file, AUTO_TO or --to")
    msg = build_email(totals, bad, sender, to)
    if dry_run:
        print(f"would send to {to}: {msg['Subject']}")
        print(msg.get_content())
        return {"sent": False, "bad_lines": bad}
    if transport is None:
        raise RuntimeError("no mail transport configured")
    transport.send_message(msg)
    print(f"sent to {to}: {msg['Subject']}")
    return {"sent": True, "bad_lines": bad}


# ============================================================================ task 3: cleanup (p013)

def is_inside(child, parent):
    child, parent = Path(child).resolve(), Path(parent).resolve()
    return parent == child or parent in child.parents


def refuse_dangerous_root(root):
    resolved = Path(root).resolve()
    if not resolved.is_dir():
        raise ValueError(f"{root} is not a folder")
    if resolved == Path(resolved.anchor) or resolved == Path.home().resolve():
        raise ValueError(f"refusing to clean {resolved}")
    return resolved


def delete_older_than(root, days, now, dry_run=True):
    base = refuse_dangerous_root(root)
    if days < 0:
        raise ValueError("days must not be negative")
    cutoff = (now - timedelta(days=days)).timestamp()
    old = []
    for folder, _dirs, files in os.walk(base):
        for name in files:
            p = Path(folder) / name
            if p.is_symlink() or not p.is_file() or not is_inside(p, base):
                continue
            if p.stat().st_mtime < cutoff:
                old.append(p)
    old.sort()
    if not dry_run:
        for p in old:
            p.unlink()
    return old


def cleanup_task(folder, days, now, yes=False):
    old = delete_older_than(folder, days, now, dry_run=not yes)
    base = Path(folder).resolve()
    label = "deleted" if yes else "would delete"
    for p in old:
        print(f"{label}: {p.relative_to(base).as_posix()}")
    return {"files": len(old), "deleted": yes}


# ============================================================================ the command line

def build_parser():
    p = argparse.ArgumentParser(prog="auto", description="My personal automation suite.")
    p.add_argument("--config", help="TOML settings file")
    p.add_argument("--status-dir", help="where status files and the lock live")
    p.add_argument("-v", "--verbose", action="count", default=0)
    sub = p.add_subparsers(dest="command", required=True)

    t = sub.add_parser("tidy", help="sort a folder into subfolders by type (undo with --undo)")
    t.add_argument("folder", type=Path)
    t.add_argument("-n", "--dry-run", action="store_true")
    t.add_argument("--undo", action="store_true", help="reverse the last tidy")

    r = sub.add_parser("report", help="summarize a sales CSV and e-mail it")
    r.add_argument("csv_file", type=Path)
    r.add_argument("--to", help="recipient (overrides the settings)")
    r.add_argument("-n", "--dry-run", action="store_true", help="print the e-mail instead of sending it")

    c = sub.add_parser("cleanup", help="delete old files (dry run unless --yes)")
    c.add_argument("folder", type=Path)
    c.add_argument("--days", type=int, help="older than this many days (overrides the settings)")
    c.add_argument("--yes", action="store_true", help="really delete")
    return p


def main(argv=None, env=None, transport=None, now=None):
    args = build_parser().parse_args(argv)
    setup_logging(args.verbose)
    flags = {"status_dir": args.status_dir, "keep_days": getattr(args, "days", None), "to": getattr(args, "to", None)}
    try:
        settings = load_settings(args.config, env, flags)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as e:
        print(f"auto: error: {e}", file=sys.stderr)
        return 2
    setup_logging(args.verbose, settings["log_file"] or None)
    clock = (lambda: now) if now is not None else (lambda: datetime.now(timezone.utc))
    status_dir = Path(settings["status_dir"])
    status_dir.mkdir(parents=True, exist_ok=True)

    if args.command == "tidy":
        job = lambda: tidy_task(args.folder, args.dry_run, args.undo)                       # noqa: E731
    elif args.command == "report":
        job = lambda: report_task(args.csv_file, settings["sender"], settings["to"], transport, args.dry_run)  # noqa: E731
    else:
        job = lambda: cleanup_task(args.folder, settings["keep_days"], clock(), args.yes)  # noqa: E731

    try:
        with single_instance(status_dir / "auto.lock"):
            return run_job(args.command, job, status_dir, clock)
    except AlreadyRunning as e:
        print(f"auto: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
