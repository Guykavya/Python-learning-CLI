# Chapter 11 (SWE): Automation and scripting

Every working developer has a folder of small scripts: one renames files, one prepares a weekly report, one downloads something every morning. These scripts are rarely beautiful, and they are some of the most valuable code you will write, because each one gives you back hours of your life. They are also where beginners lose data: a script that moves, renames or deletes files does it **fast, without asking, and on the wrong folder** exactly once, and that once is enough.

This chapter teaches how to write automation that is **useful and safe**: command-line tools with good arguments and exit codes, scripts that can be tested and that show what they will do before doing it, file and system automation that can be undone, web and browser automation that is polite and robust, and scheduling so that the work happens without you.

By the end you reach this outcome: **you can automate a repetitive task that you really do every week** (section 2 helps you pick it, section 16 is the project), and you can explain why your script is safe to run twice.

Prerequisites: core.17 (files and the standard library tour) and the testing habits from core.08. You do not need a web framework for this chapter.

> **Offline rule for this chapter.** The exercises run on the standard library (`argparse`, `pathlib`, `shutil`, `subprocess`, `logging`, `http.server`, `html.parser`) and on `click`, which is installed. **Typer, rich and Playwright are not installed** in the course environment, and a browser cannot be assumed. They appear as code to read and as clearly marked **Try it on your machine** steps with exact commands and **no invented output**. Every other output was produced by running the code above it, with these versions (timings and temporary paths differ on your machine):

```bash run
python -c "
import sys, click, platform
print('python  ', sys.version.split()[0])
print('click   ', click.__version__)
print('system  ', platform.system())
"
```
```text
python   3.14.4
click    8.5.1
system   Linux
<string>:4: DeprecationWarning: The '__version__' attribute is deprecated and will be removed in Click 9.1. Use feature detection or 'importlib.metadata.version("click")' instead.
```

## Table of contents

1. [What automation is for, and what it costs](#1-what-automation-is-for-and-what-it-costs)
2. [Anatomy of a script you can trust](#2-anatomy-of-a-script-you-can-trust)
3. [A real tool with argparse: tidy](#3-a-real-tool-with-argparse-tidy)
4. [Testing a command-line tool](#4-testing-a-command-line-tool)
5. [Click, Typer and rich](#5-click-typer-and-rich)
6. [Files and folders in depth](#6-files-and-folders-in-depth)
7. [Running other programs: subprocess](#7-running-other-programs-subprocess)
8. [Configuration, secrets and logging for scripts](#8-configuration-secrets-and-logging-for-scripts)
9. [Data automation: from a CSV to a weekly e-mail](#9-data-automation-from-a-csv-to-a-weekly-e-mail)
10. [Web automation without a browser](#10-web-automation-without-a-browser)
11. [Browser automation with Playwright](#11-browser-automation-with-playwright)
12. [Scheduling: running scripts without you](#12-scheduling-running-scripts-without-you)
13. [Making scheduled jobs reliable](#13-making-scheduled-jobs-reliable)
14. [Packaging and sharing your tools](#14-packaging-and-sharing-your-tools)
15. [Structuring a personal automation suite](#15-structuring-a-personal-automation-suite)
16. [Project: your personal automation suite](#16-project-your-personal-automation-suite)
17. [Common traps](#17-common-traps)
18. [Collected traps](#18-collected-traps)
19. [Summary](#19-summary)

## 1. What automation is for, and what it costs

### 1.1 The payoff formula

Automating something costs time now and saves time later. Before you start, do the arithmetic:

```text
saved per year  =  (minutes per run)  x  (runs per year)
worth it if      saved per year  >  (minutes to write + test + maintain)  x  2 or 3
```

The factor of 2 or 3 is honest: scripts always take longer than planned, and they break when the world changes (a website changes its layout, a folder moves). A task you do for 10 minutes every week is 520 minutes a year. A script that takes three hours to write and one hour a year to fix saves you about 4 hours a year, which is a good deal. A task you do once a year for 5 minutes is **not** worth scripting; write down the steps instead.

```bash run
python -c "
def worth_it(minutes_per_run, runs_per_year, minutes_to_build, minutes_upkeep_per_year=60, years=2):
    saved = minutes_per_run * runs_per_year * years
    cost = minutes_to_build + minutes_upkeep_per_year * years
    return saved, cost, saved > 2 * cost
for name, args in [('weekly 10-minute report', (10, 52, 180)),
                   ('yearly 5-minute form', (5, 1, 120)),
                   ('daily 2-minute download', (2, 250, 90))]:
    saved, cost, ok = worth_it(*args)
    print(f'{name:26} saves {saved:5} min, costs {cost:4} min -> automate: {ok}')
"
```
```text
weekly 10-minute report    saves  1040 min, costs  300 min -> automate: True
yearly 5-minute form       saves    10 min, costs  240 min -> automate: False
daily 2-minute download    saves  1000 min, costs  210 min -> automate: True
```

### 1.2 Levels of automation

Not every task needs a Python program. Climb only as high as the task requires:

| Level | Tool | Good for |
|---|---|---|
| 0 | A written checklist | rare tasks, tasks needing judgement |
| 1 | A shell alias or one-liner | one command you retype often |
| 2 | A short Python script | file work, data cleaning, glue between tools |
| 3 | A CLI tool with arguments, tests and logging | something you or others run weekly |
| 4 | A scheduled, monitored job | something that must happen without you |

This chapter goes from level 2 to level 4.

### 1.3 The four rules of safe automation

Keep these four rules in mind through the whole chapter. Almost every automation disaster breaks one of them.

1. **Look before you leap.** Provide a `--dry-run` that prints what would happen and changes nothing.
2. **Be able to undo.** Move to a folder (or a trash) instead of deleting. Keep a journal of what you changed.
3. **Be safe to run twice.** The second run should do nothing or the same thing, never the damage twice (idempotent, as in swe.08).
4. **Fail loudly.** A non-zero exit code and a clear message, never a silent half-finished job.

### Try it: pick your task

List three things you do on a computer more than once a month. For each, estimate minutes per run and runs per year, and apply the formula. Which one wins?

<details><summary>Answer</summary>

There is no fixed answer. A good candidate is boring, frequent, rule-based and has a result you can check (a renamed file, a generated report). Poor candidates need human judgement ("reply to e-mails") or happen rarely. Keep your winner: it becomes the project in section 16.

</details>

## 2. Anatomy of a script you can trust

### 2.1 A first script, and what is wrong with it

Here is what most first scripts look like:

```python
# bad_tidy.py   (do not run on a real folder)
import os, shutil
folder = "C:/Users/me/Downloads"
for f in os.listdir(folder):
    if f.endswith(".pdf"):
        shutil.move(folder + "/" + f, folder + "/pdfs/" + f)
```

Problems, in order of seriousness:

- The folder is **hard-coded**: to use it elsewhere you edit the code.
- If `pdfs/` does not exist, it crashes halfway; if a file with the same name is already there, the move **overwrites** it (silently, on some systems).
- No dry-run, no log, no undo.
- It runs when imported, so you cannot test it.
- Paths are glued with `+` and `/`, which breaks on Windows (or Linux) in surprising ways.

### 2.2 The skeleton to copy

Almost every good script has this shape:

```python
import argparse
import logging
import sys
from pathlib import Path

log = logging.getLogger("mytool")


def do_the_work(folder: Path, dry_run: bool) -> int:
    """Pure-ish function: takes values, returns a result. Easy to test."""
    ...


def build_parser():
    p = argparse.ArgumentParser(prog="mytool", description="One sentence about what it does.")
    p.add_argument("folder", type=Path)
    p.add_argument("-n", "--dry-run", action="store_true")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        return do_the_work(args.folder, args.dry_run)
    except KeyboardInterrupt:
        return 130
    except OSError as e:
        log.error("%s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

Why each piece exists:

| Piece | Reason |
|---|---|
| `main(argv=None)` | tests can call `main(["x", "--dry-run"])` without a subprocess |
| `if __name__ == "__main__"` | importing the file does not run it |
| `sys.exit(main())` | the return value becomes the **exit code** the shell and cron see |
| logic in separate functions | testable without arguments or a terminal |
| `pathlib.Path` | correct on every operating system |
| `logging`, not `print`, for diagnostics | levels, timestamps, files; `print` is for the tool's real output |
| `except OSError` at the edge | expected failures become a clean message, bugs still show a traceback |

### 2.3 Exit codes are the script's real answer

A program does not "return text" to the shell; it returns an **exit code**. `0` means success, anything else means failure. Cron, CI, `make` and `&&` all rely on it.

| Code | Meaning (convention) |
|---|---|
| 0 | success |
| 1 | general failure |
| 2 | wrong usage (argparse uses this) |
| 130 | stopped with Ctrl+C |

Watch the shell use them:

```bash run
python -c "import sys; sys.exit(0)" && echo "first command worked, so this ran"
python -c "import sys; sys.exit(3)" && echo "this is never printed"
echo "exit code of the last command: $?"
```
```text
first command worked, so this ran
exit code of the last command: 3
```

### 2.4 stdout, stderr and the pipe

A tool's real output goes to **stdout**; messages for the human (progress, errors) go to **stderr**. That lets people write `mytool list > out.txt` and still see errors on the screen, and it lets other programs read your output cleanly.

```bash run
python -c "
import sys
print('data line 1'); print('data line 2')
print('warning: something odd', file=sys.stderr)
" > captured.txt
echo '--- what was captured from stdout:'
cat captured.txt
```
```text
--- what was captured from stdout:
data line 1
data line 2
warning: something odd
```

### Try it: what is wrong?

A script prints `Processing 120 files...` with `print()` and then the list of results with `print()`. A colleague runs `script.py | sort` and gets a strange first line. Why, and what is the fix?

<details><summary>Answer</summary>

The progress message went to stdout together with the data, so `sort` sorted it into the results. Send diagnostics to **stderr** (`print(..., file=sys.stderr)` or `logging`) and keep stdout for data only.

</details>

## 3. A real tool with argparse: tidy

We build one tool through the chapter. **tidy** organizes a messy folder into subfolders by file type, can show a dry run, can undo, and can find duplicate files. First the logic, with **no command-line code at all**, so it is easy to test. It follows the four rules: it moves instead of deleting, writes a journal for undo, never overwrites, and is safe to run twice.

```python
# tidylib.py
import hashlib
import json
import shutil
from pathlib import Path

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


def plan_moves(root):
    """Decide what to move where. Changes nothing. Only files directly in `root`, no hidden ones."""
    moves = []
    for src in sorted(Path(root).iterdir()):
        if src.is_file() and not src.name.startswith("."):
            moves.append((src, unique_destination(Path(root) / category_for(src) / src.name)))
    return moves


def apply_moves(moves, root, dry_run=False):
    """Do the moves (unless dry_run) and write a journal so they can be undone."""
    done = []
    for src, dst in moves:
        if not dry_run:
            dst.parent.mkdir(exist_ok=True)
            shutil.move(str(src), str(dst))
        done.append((src, dst))
    if done and not dry_run:
        (Path(root) / JOURNAL).write_text(json.dumps([[str(s), str(d)] for s, d in done]))
    return done


def undo(root):
    """Put every file back where the journal says it came from."""
    journal = Path(root) / JOURNAL
    if not journal.exists():
        return []
    restored = []
    for s, d in reversed(json.loads(journal.read_text())):
        s, d = Path(s), Path(d)
        if d.exists() and not s.exists():
            shutil.move(str(d), str(s))
            restored.append((d, s))
            try:
                d.parent.rmdir()                    # remove the category folder if it is now empty
            except OSError:
                pass                                # not empty: leave it alone
    journal.unlink()
    return restored


def sha256_of(path, chunk=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:                     # read in chunks: works for huge files
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def find_duplicates(root, min_size=1):
    """Groups of files with identical content. Cheap check (size) first, expensive hash second."""
    by_size = {}
    for p in Path(root).rglob("*"):
        if p.is_file() and not p.is_symlink() and p.stat().st_size >= min_size:
            by_size.setdefault(p.stat().st_size, []).append(p)
    groups = []
    for paths in by_size.values():
        if len(paths) > 1:
            by_hash = {}
            for p in paths:
                by_hash.setdefault(sha256_of(p), []).append(p)
            groups += [sorted(g) for g in by_hash.values() if len(g) > 1]
    return sorted(groups)
```

Now the command line. `argparse` is in the standard library, needs no install, and is enough for most tools. **Subcommands** (`tidy organize`, `tidy undo`) keep one tool with several jobs:

```python
# tidy.py
import argparse
import sys
from pathlib import Path

import tidylib


def build_parser():
    p = argparse.ArgumentParser(prog="tidy", description="Tidy a folder safely.")
    p.add_argument("--version", action="version", version="tidy 1.0")
    sub = p.add_subparsers(dest="command", required=True)

    org = sub.add_parser("organize", help="move files into folders by type")
    org.add_argument("folder", type=Path)
    org.add_argument("-n", "--dry-run", action="store_true", help="show what would happen, change nothing")

    und = sub.add_parser("undo", help="reverse the last 'organize'")
    und.add_argument("folder", type=Path)

    dup = sub.add_parser("dupes", help="list files with identical content")
    dup.add_argument("folder", type=Path)
    dup.add_argument("--min-size", type=int, default=1, metavar="BYTES", help="ignore smaller files")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.folder.is_dir():
        print(f"tidy: error: {args.folder} is not a folder", file=sys.stderr)
        return 1
    if args.command == "organize":
        moves = tidylib.apply_moves(tidylib.plan_moves(args.folder), args.folder, args.dry_run)
        label = "would move" if args.dry_run else "moved"
        for src, dst in moves:
            print(f"{label}: {src.name} -> {dst.relative_to(args.folder)}")
        print(f"{len(moves)} file(s) {label.replace('would move', 'to move')}", file=sys.stderr)
    elif args.command == "undo":
        restored = tidylib.undo(args.folder)
        print(f"restored {len(restored)} file(s)")
    else:
        groups = tidylib.find_duplicates(args.folder, args.min_size)
        for g in groups:
            print(" == ".join(str(p.relative_to(args.folder)) for p in g))
        print(f"{len(groups)} group(s) of duplicates", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

A script to build a deterministic messy folder (so every run of this chapter looks the same):

```python
# make_mess.py
import sys
from pathlib import Path

root = Path(sys.argv[1])
root.mkdir(exist_ok=True)
files = {
    "holiday.JPG": b"jpeg-bytes-1", "logo.png": b"png-bytes", "invoice-march.pdf": b"pdf-march",
    "invoice-april.pdf": b"pdf-april", "notes.txt": b"my notes", "notes-copy.txt": b"my notes",
    "sales.csv": b"a,b\n1,2\n", "backup.zip": b"zip-bytes", "song.mp3": b"mp3-bytes",
    "README": b"no extension", ".hidden": b"secret",
}
for name, data in files.items():
    (root / name).write_bytes(data)
print(f"created {len(files)} files in {root}")
```

Try it. First **ask for help** (argparse writes it for you), then a **dry run**, which must change nothing:

```bash run
python make_mess.py mess
python tidy.py --help
echo "-----"
python tidy.py organize mess --dry-run
echo "-----  folder after the dry run (unchanged):"
ls -A mess
```
```text
created 11 files in mess
usage: tidy [-h] [--version] {organize,undo,dupes} ...

Tidy a folder safely.

positional arguments:
  {organize,undo,dupes}
    organize            move files into folders by type
    undo                reverse the last 'organize'
    dupes               list files with identical content

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
-----
would move: README -> other/README
would move: backup.zip -> archives/backup.zip
would move: holiday.JPG -> images/holiday.JPG
would move: invoice-april.pdf -> documents/invoice-april.pdf
would move: invoice-march.pdf -> documents/invoice-march.pdf
would move: logo.png -> images/logo.png
would move: notes-copy.txt -> documents/notes-copy.txt
would move: notes.txt -> documents/notes.txt
would move: sales.csv -> data/sales.csv
would move: song.mp3 -> audio/song.mp3
-----  folder after the dry run (unchanged):
.hidden
README
backup.zip
holiday.JPG
invoice-april.pdf
invoice-march.pdf
logo.png
notes-copy.txt
notes.txt
sales.csv
song.mp3
10 file(s) to move
```

Now do it for real, run it **again** (rule 3: safe to run twice), and then undo:

```bash run
python tidy.py organize mess
echo "----- second run:"
python tidy.py organize mess
echo "----- tree after organizing:"
find mess -type f -not -name ".tidy-journal.json" | sort
echo "----- undo:"
python tidy.py undo mess
ls -A mess
```
```text
moved: README -> other/README
moved: backup.zip -> archives/backup.zip
moved: holiday.JPG -> images/holiday.JPG
moved: invoice-april.pdf -> documents/invoice-april.pdf
moved: invoice-march.pdf -> documents/invoice-march.pdf
moved: logo.png -> images/logo.png
moved: notes-copy.txt -> documents/notes-copy.txt
moved: notes.txt -> documents/notes.txt
moved: sales.csv -> data/sales.csv
moved: song.mp3 -> audio/song.mp3
----- second run:
----- tree after organizing:
mess/archives/backup.zip
mess/audio/song.mp3
mess/data/sales.csv
mess/documents/invoice-april.pdf
mess/documents/invoice-march.pdf
mess/documents/notes-copy.txt
mess/documents/notes.txt
mess/.hidden
mess/images/holiday.JPG
mess/images/logo.png
mess/other/README
----- undo:
restored 10 file(s)
.hidden
README
backup.zip
holiday.JPG
invoice-april.pdf
invoice-march.pdf
logo.png
notes-copy.txt
notes.txt
sales.csv
song.mp3
10 file(s) moved
0 file(s) moved
```

Three things to notice. The dry run really changed nothing. The second run found nothing more to move (the journal is hidden, so it is ignored; the files already sit in subfolders). And `undo` returned every file to its place. When a tool gives you these three guarantees, you can run it on a real folder without fear.

Duplicates, and what happens when the usage is wrong (argparse exits with code 2 by itself):

```bash run
python tidy.py dupes mess
echo "-----  a typo in the command (exit code shown below):"
python tidy.py organise mess
```
```text
notes-copy.txt == notes.txt
-----  a typo in the command (exit code shown below):
1 group(s) of duplicates
usage: tidy [-h] [--version] {organize,undo,dupes} ...
tidy: error: argument command: invalid choice: 'organise' (choose from organize, undo, dupes)
```

```bash run
python tidy.py organise mess; echo "exit code: $?"
python tidy.py organize no-such-folder; echo "exit code: $?"
```
```text
exit code: 2
exit code: 1
usage: tidy [-h] [--version] {organize,undo,dupes} ...
tidy: error: argument command: invalid choice: 'organise' (choose from organize, undo, dupes)
tidy: error: no-such-folder is not a folder
```

### 3.1 argparse in one table

| You want | Write |
|---|---|
| a required positional argument | `p.add_argument("folder", type=Path)` |
| an on/off flag | `p.add_argument("-n", "--dry-run", action="store_true")` |
| a counted flag (`-vv`) | `action="count", default=0` |
| a number with a default | `type=int, default=10` |
| a choice from a list | `choices=["csv", "json"]` |
| many values | `nargs="+"` |
| either/or options | `g = p.add_mutually_exclusive_group()` |
| a version flag | `action="version", version="tool 1.0"` |
| input from a file or stdin | `type=argparse.FileType("r")`, and `-` means stdin |

Prefer `type=Path` so your function gets a `Path`, and let argparse validate numbers and choices: the error message and exit code 2 come for free.

### Try it: add a flag

Add `--by-date` to `organize` so files go to `2026-11/...` folders using their modification time instead of type. Which functions change, and which stay the same?

<details><summary>Answer</summary>

Add the flag in `build_parser`, pass it to `plan_moves(root, by_date=False)`, and compute the folder name there (`datetime.fromtimestamp(src.stat().st_mtime).strftime("%Y-%m")`). `apply_moves`, `undo` and the journal stay the same, because they only deal with (source, destination) pairs. That is the benefit of separating *planning* from *doing*: a dry run is simply "plan, then print".

</details>

## 4. Testing a command-line tool

A script you cannot test is a script you are afraid to change. Because `main(argv)` takes arguments and returns an exit code, and the logic lives in `tidylib`, tests are short. We use pytest's `tmp_path` (a fresh temporary folder per test) and `capsys` (captures printed output).

```python
# test_tidy.py
import pytest

import tidy
import tidylib


@pytest.fixture
def messy(tmp_path):
    for name, data in {"a.pdf": b"pdf", "b.PNG": b"png", "c": b"none", ".hidden": b"h"}.items():
        (tmp_path / name).write_bytes(data)
    return tmp_path


def test_category_ignores_case_and_defaults_to_other():
    assert tidylib.category_for("x.PNG") == "images"
    assert tidylib.category_for("README") == "other"


def test_dry_run_changes_nothing(messy, capsys):
    before = sorted(p.name for p in messy.iterdir())
    assert tidy.main(["organize", str(messy), "--dry-run"]) == 0
    assert sorted(p.name for p in messy.iterdir()) == before, "a dry run must not touch the disk"
    assert "would move: a.pdf -> documents" in capsys.readouterr().out


def test_organize_moves_and_skips_hidden(messy):
    tidy.main(["organize", str(messy)])
    assert (messy / "documents" / "a.pdf").exists()
    assert (messy / "images" / "b.PNG").exists()
    assert (messy / ".hidden").exists(), "hidden files stay where they are"


def test_never_overwrites(tmp_path):
    (tmp_path / "documents").mkdir()
    (tmp_path / "documents" / "a.pdf").write_bytes(b"OLD")
    (tmp_path / "a.pdf").write_bytes(b"NEW")
    tidy.main(["organize", str(tmp_path)])
    assert (tmp_path / "documents" / "a.pdf").read_bytes() == b"OLD", "the existing file must survive"
    assert (tmp_path / "documents" / "a (1).pdf").read_bytes() == b"NEW"


def test_running_twice_is_harmless(messy, capsys):
    tidy.main(["organize", str(messy)])
    capsys.readouterr()
    tidy.main(["organize", str(messy)])
    assert "0 file(s) moved" in capsys.readouterr().err, "the second run must find nothing to do"


def test_undo_restores_everything(messy):
    before = sorted(p.name for p in messy.iterdir())
    tidy.main(["organize", str(messy)])
    tidy.main(["undo", str(messy)])
    assert sorted(p.name for p in messy.iterdir()) == before


def test_missing_folder_is_exit_code_1(tmp_path, capsys):
    assert tidy.main(["organize", str(tmp_path / "nope")]) == 1
    assert "not a folder" in capsys.readouterr().err


def test_usage_error_is_exit_code_2():
    with pytest.raises(SystemExit) as e:
        tidy.main(["organise", "x"])
    assert e.value.code == 2


def test_duplicates_are_found_by_content_not_name(tmp_path):
    (tmp_path / "one.txt").write_bytes(b"same")
    (tmp_path / "two.bin").write_bytes(b"same")
    (tmp_path / "three.txt").write_bytes(b"different")
    groups = tidylib.find_duplicates(tmp_path)
    assert [[p.name for p in g] for g in groups] == [["one.txt", "two.bin"]]
```

```bash run
python -m pytest -q -p no:cacheprovider test_tidy.py
```
```text
.........                                                                [100%]
9 passed in 0.10s
```

Nine of these tests would be terrifying to run by hand against a real folder; here they take milliseconds and cannot hurt anything, because `tmp_path` is a throwaway.

### Try it: the test that proves it

Which test would catch it if someone changed `unique_destination` to simply return `dst`?

<details><summary>Answer</summary>

`test_never_overwrites`: the second `a.pdf` would replace the first, so the `OLD` content would be gone. This is why a safety rule deserves its own test with a message that names the mistake.

</details>

## 5. Click, Typer and rich

`argparse` is enough, but it is verbose. Two popular libraries make command-line tools nicer to write.

### 5.1 Click

**Click** uses decorators. It also gives you colours, prompts, confirmations, progress bars and a built-in test runner. It is installed here, so the next example really runs. The same `organize` and `undo` as above:

```python
# tidy_click.py
from pathlib import Path

import click

import tidylib


@click.group()
@click.version_option("1.0", prog_name="tidy")
def cli():
    """Tidy a folder safely."""


@cli.command()
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("-n", "--dry-run", is_flag=True, help="Show what would happen, change nothing.")
def organize(folder, dry_run):
    """Move files into folders by type."""
    moves = tidylib.apply_moves(tidylib.plan_moves(folder), folder, dry_run)
    for src, dst in moves:
        click.echo(f"{'would move' if dry_run else 'moved'}: {src.name} -> {dst.relative_to(folder)}")


@cli.command()
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.confirmation_option(prompt="Put all moved files back?")
def undo(folder):
    """Reverse the last organize."""
    click.echo(f"restored {len(tidylib.undo(folder))} file(s)")


if __name__ == "__main__":
    cli()
```

Differences you can see: `click.Path(exists=True, file_okay=False)` validates the folder for you; `confirmation_option` asks "are you sure?" before a risky command and supports `--yes`. Click ships a test runner, so no subprocess is needed:

```bash run
python make_mess.py mess2 > /dev/null
python tidy_click.py --help
python - <<'EOF'
from click.testing import CliRunner
from tidy_click import cli

runner = CliRunner()
r = runner.invoke(cli, ["organize", "mess2", "--dry-run"])
print("exit code:", r.exit_code)
print(r.output.strip().splitlines()[0])
r = runner.invoke(cli, ["undo", "mess2"], input="n\n")          # answer 'no' to the question
print("answered no -> exit code", r.exit_code, "| output:", r.output.strip().splitlines()[-1])
r = runner.invoke(cli, ["organize", "no-such-folder"])
print("missing folder -> exit code", r.exit_code, "|", r.output.strip().splitlines()[-1])
EOF
```
```text
Usage: tidy_click.py [OPTIONS] COMMAND [ARGS]...

  Tidy a folder safely.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  organize  Move files into folders by type.
  undo      Reverse the last organize.
exit code: 0
would move: README -> other/README
answered no -> exit code 1 | output: Aborted!
missing folder -> exit code 2 | Error: Invalid value for 'FOLDER': Directory 'no-such-folder' does not exist.
```

### 5.2 Typer

**Typer** is built on Click and uses **type hints** instead of decorators for the arguments, exactly like FastAPI uses them for requests (swe.05). It is the most pleasant choice for new tools. This is the same tool in Typer. It is not installed here, so read it and try it on your machine:

```python
# tidy_typer.py  (needs: pip install typer)
from pathlib import Path
from typing import Annotated

import typer

import tidylib

app = typer.Typer(help="Tidy a folder safely.", no_args_is_help=True)


@app.command()
def organize(
    folder: Annotated[Path, typer.Argument(exists=True, file_okay=False)],
    dry_run: Annotated[bool, typer.Option("--dry-run", "-n", help="Change nothing.")] = False,
):
    """Move files into folders by type."""
    for src, dst in tidylib.apply_moves(tidylib.plan_moves(folder), folder, dry_run):
        typer.echo(f"{'would move' if dry_run else 'moved'}: {src.name} -> {dst.relative_to(folder)}")


@app.command()
def undo(folder: Annotated[Path, typer.Argument(exists=True, file_okay=False)]):
    """Reverse the last organize."""
    typer.echo(f"restored {len(tidylib.undo(folder))} file(s)")


if __name__ == "__main__":
    app()
```

**Try it on your machine:** `pip install typer`, save the file next to `tidylib.py`, then run `python tidy_typer.py --help`, `python tidy_typer.py organize some_folder --dry-run`, and `python tidy_typer.py --install-completion` (it adds shell tab-completion). Typer's test helper is `typer.testing.CliRunner`, the same as Click's.

### 5.3 rich

**rich** makes terminal output readable: tables, colours, progress bars, tracebacks. Example (not installed here; run it on your machine after `pip install rich`):

```python
# report_rich.py  (needs: pip install rich)
from rich.console import Console
from rich.progress import track
from rich.table import Table

console = Console()
table = Table(title="Moved files")
table.add_column("File")
table.add_column("Folder", style="cyan")
table.add_row("invoice.pdf", "documents")
table.add_row("holiday.jpg", "images")
console.print(table)

for _ in track(range(50), description="Hashing..."):
    pass
console.print("[bold green]done[/bold green]")
```

Two rules for fancy output: it must **degrade** when the output is not a terminal (rich does this automatically: no colours when piped), and **data** goes to stdout without decoration so other programs can read it. You can get a plain table with no library at all, and it works everywhere:

```python run
def table(rows, headers):
    widths = [max(len(str(x)) for x in col) for col in zip(headers, *rows)]
    line = lambda r: "  ".join(str(x).ljust(w) for x, w in zip(r, widths))
    print(line(headers))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print(line(r))


table([("invoice.pdf", "documents", 12_300), ("holiday.jpg", "images", 2_400_000)],
      ["file", "folder", "bytes"])
```
```text
file         folder     bytes  
-----------  ---------  -------
invoice.pdf  documents  12300  
holiday.jpg  images     2400000
```

### 5.4 Which to choose?

| Tool | Choose it when |
|---|---|
| `argparse` | a small script, no dependencies allowed (cron on a server, a standalone `.py` you send to a friend) |
| `click` | a larger tool with many subcommands, prompts, colours |
| `typer` | you like type hints (and already know FastAPI); great defaults and completion |
| `rich` | any of the above, for tables and progress; output is for humans |

Whichever you pick, keep the logic in plain functions (like `tidylib`); the CLI layer should be thin. Switching libraries then costs 20 lines.

### Try it: spot the thin layer

In which file would you fix a bug where `.JPG` files are put in `other`? Which file would you edit to rename `--dry-run` to `--preview`?

<details><summary>Answer</summary>

The first is in `tidylib.py` (`category_for` lower-cases the suffix; check the `CATEGORIES` table). The second is only in the CLI file. If a change to one kind of thing forces you to edit both kinds of file, your layers are tangled (compare swe.10).

</details>

## 6. Files and folders in depth

Most automation is file work. `pathlib` is the modern tool; `shutil` copies and moves; `tempfile` makes safe scratch space. All examples run in throw-away folders.

### 6.1 pathlib in ten lines

```python run
from pathlib import Path
import tempfile

root = Path(tempfile.mkdtemp())
report = root / "reports" / "2026" / "march.csv"       # / joins paths, on every OS
report.parent.mkdir(parents=True, exist_ok=True)       # make all missing folders; no error if present
report.write_text("id,total\n1,10\n2,20\n")

print("name  :", report.name)
print("stem  :", report.stem)
print("suffix:", report.suffix)
print("parent:", report.parent.name)
print("exists:", report.exists(), "| is_file:", report.is_file(), "| size:", report.stat().st_size)
print("text  :", report.read_text().splitlines())
print("with_suffix:", report.with_suffix(".json").name)
print("glob  :", sorted(p.name for p in root.rglob("*.csv")))
print("relative:", report.relative_to(root))
```
```text
name  : march.csv
stem  : march
suffix: .csv
parent: 2026
exists: True | is_file: True | size: 19
text  : ['id,total', '1,10', '2,20']
with_suffix: march.json
glob  : ['march.csv']
relative: reports/2026/march.csv
```

### 6.2 Traps with paths and files

| Trap | Why it bites | Safer |
|---|---|---|
| `"folder" + "/" + name` | breaks on Windows, double slashes | `Path(folder) / name` |
| `os.listdir()` and sorting by hand | arbitrary order, strings not paths | `sorted(Path.iterdir())` |
| `rglob("*")` follows into huge trees | slow, surprising | filter early; skip `.git`, `node_modules`, symlinks |
| Moving across drives | `rename` fails; `shutil.move` copies then deletes | use `shutil.move` |
| Overwriting by accident | `shutil.copy`/`move` may replace silently | check `exists()` first, or use a unique name (section 3) |
| Reading a huge file with `.read_text()` | memory | iterate lines or read in chunks |
| Case-insensitive file systems | `A.txt` and `a.txt` are the same on Windows and macOS | compare lower-cased names |
| Relative paths in cron | cron's working directory is not yours | use absolute paths, or `Path(__file__).resolve().parent` |
| Text encoding | the default differs between systems | `read_text(encoding="utf-8")` always |

### 6.3 Writing a file so a crash cannot leave half a file

If your script dies while writing `report.json`, you are left with a truncated file that the next run may read as valid. Write to a temporary file in the same folder, then **atomically replace** the target. A reader sees either the old file or the new one, never half of it:

```python run
import os
import tempfile
from pathlib import Path


def atomic_write_text(path, text):
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())               # make sure the bytes reached the disk
        os.replace(tmp, path)                  # atomic on the same file system
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


target = Path(tempfile.mkdtemp()) / "state.json"
atomic_write_text(target, '{"last_run": 1}')
atomic_write_text(target, '{"last_run": 2}')
print(target.read_text(), "| leftover temp files:", [p.name for p in target.parent.glob("*.tmp")])
```
```text
{"last_run": 2} | leftover temp files: []
```

### 6.4 Deleting safely

Deleting is the one operation that cannot be undone, so:

- **Prefer moving to a trash folder** you control, with a date: `trash/2026-11-09/`. Empty it with a separate, boring command after a week.
- If you must delete, **print what you will delete first** and ask (`input()` or Click's confirmation) unless `--yes` is given.
- Never build a delete path by string concatenation from user input; check that the resolved path is **inside** the folder you expect:

```python run
from pathlib import Path


def is_inside(child, parent):
    child, parent = Path(child).resolve(), Path(parent).resolve()
    return parent == child or parent in child.parents


base = Path("/tmp/sandbox")
print(is_inside("/tmp/sandbox/a/b.txt", base))
print(is_inside("/tmp/sandbox/../etc/passwd", base), "<- a '..' escape is caught because we resolve() first")
```
```text
True
False <- a '..' escape is caught because we resolve() first
```

### 6.5 Watching a folder, and archives

- To react to new files you can **poll** (list the folder every few seconds and compare with last time), which needs no library, or use `watchdog` (`pip install watchdog`) for real-time events. Polling every 5 to 30 seconds is plenty for almost every personal task.
- `shutil.make_archive("backup", "zip", root_dir)` creates a zip; `shutil.unpack_archive` reads one. For incremental backups prefer `rsync` (Linux/macOS) or `robocopy` (Windows) over reinventing it.

A polling "what changed since last time" function, which is also the basis of many sync tools:

```python run
import tempfile
from pathlib import Path


def snapshot(root):
    return {str(p.relative_to(root)): (p.stat().st_size, int(p.stat().st_mtime)) for p in root.rglob("*") if p.is_file()}


def changes(old, new):
    return {"added": sorted(new.keys() - old.keys()),
            "removed": sorted(old.keys() - new.keys()),
            "modified": sorted(k for k in old.keys() & new.keys() if old[k] != new[k])}


root = Path(tempfile.mkdtemp())
(root / "a.txt").write_text("1")
(root / "b.txt").write_text("22")
before = snapshot(root)
(root / "a.txt").write_text("123456")          # modified (different size)
(root / "b.txt").unlink()                      # removed
(root / "c.txt").write_text("new")             # added
print(changes(before, snapshot(root)))
```
```text
{'added': ['c.txt'], 'removed': ['b.txt'], 'modified': ['a.txt']}
```

### Try it: what could go wrong?

A cleanup script runs `for p in Path(folder).rglob("*"): if p.suffix == ".tmp": p.unlink()`. The folder name comes from a config file. List two ways this could delete something you did not intend.

<details><summary>Answer</summary>

(1) The config is empty or wrong (for example `/` or the home folder), so it deletes `.tmp` files across the whole disk or home. Guard with `is_inside` against an allowed base folder and print a count first. (2) Symlinks: a `.tmp` link or folder inside the tree can point outside it. Skip `is_symlink()` entries. A third: a legitimate `.tmp` file that something else is still writing; delete only files older than a day.

</details>

## 7. Running other programs: subprocess

Automation often means gluing existing tools: `git`, `ffmpeg`, `pg_dump`, `robocopy`. The standard way is `subprocess.run`.

### 7.1 The safe way

```python run
import subprocess
import sys

# 1. A list of arguments, never one big string with shell=True.
result = subprocess.run([sys.executable, "-c", "print('hello from a child')"],
                        capture_output=True, text=True, check=True, timeout=10)
print("stdout :", result.stdout.strip())
print("code   :", result.returncode)

# 2. A failing command: check=True turns a non-zero exit code into an exception.
try:
    subprocess.run([sys.executable, "-c", "import sys; print('boom', file=sys.stderr); sys.exit(4)"],
                   capture_output=True, text=True, check=True)
except subprocess.CalledProcessError as e:
    print("failed : exit code", e.returncode, "| stderr:", e.stderr.strip())

# 3. A command that hangs: timeout kills it.
try:
    subprocess.run([sys.executable, "-c", "import time; time.sleep(30)"], timeout=0.5)
except subprocess.TimeoutExpired:
    print("timeout: the child was stopped after 0.5 s")
```
```text
stdout : hello from a child
code   : 0
failed : exit code 4 | stderr: boom
timeout: the child was stopped after 0.5 s
```

Rules:

| Rule | Reason |
|---|---|
| Pass a **list**, avoid `shell=True` | with a string and `shell=True`, a filename like `a; rm -rf ~` becomes a command (shell injection) |
| `check=True` | a failure must not be ignored |
| `capture_output=True, text=True` | to read output as text |
| Always a `timeout` for anything that might hang | a stuck child freezes the whole script |
| Use `sys.executable` to run Python | the same interpreter and environment |
| Never build commands from untrusted text | see swe.07 on injection |

The injection danger, shown safely with `echo`:

```python run
import subprocess

filename = "report.txt; echo INJECTED"
subprocess.run(f"echo processing {filename}", shell=True)           # BAD: the shell sees two commands
subprocess.run(["echo", "processing", filename])                    # GOOD: one argument, printed as text
```
```text
processing report.txt
INJECTED
processing report.txt; echo INJECTED
```

### 7.2 Pipes between programs, and live output

To stream output as it arrives (a long job), use `Popen` and read line by line. To chain commands, do it in Python (`run` twice and pass `input=`) rather than building shell pipelines. For an interactive progress display, let the child inherit the terminal by not capturing.

### 7.3 Looking at the system

`psutil` (installed here) answers "how much disk, memory, CPU is used?" and "is my process running?", which makes health-check scripts easy:

```python run
import shutil
import psutil

total, used, free = shutil.disk_usage("/")
print(f"disk free   : {free / total:6.1%}")
print(f"memory used : {psutil.virtual_memory().percent:5.1f}%")
print("cpu count   :", psutil.cpu_count())
python_procs = [p.info["pid"] for p in psutil.process_iter(["pid", "name"]) if "python" in (p.info["name"] or "").lower()]
print("python processes running:", len(python_procs) > 0)
```
```text
disk free   :  23.3%
memory used :  52.8%
cpu count   : 8
python processes running: True
```

(The numbers differ on every machine.) A disk-space warning script is a classic first automation: check `free / total`, and if it is below 10%, exit non-zero so cron or a monitor notices.

### Try it: fix the injection

`os.system("convert " + user_file + " out.png")` converts an uploaded image. Rewrite it safely.

<details><summary>Answer</summary>

`subprocess.run(["convert", user_file, "out.png"], check=True, timeout=60)`. The list form passes `user_file` as a single argument, so spaces and `;` have no special meaning. Also validate that `user_file` lies inside the expected upload folder, and consider that a file name starting with `-` could be read as an option: put `"--"` before it when the tool supports it.

</details>



## 8. Configuration, secrets and logging for scripts

### 8.1 Where settings live

A script with `folder = "C:/Users/me/Downloads"` in the code works on one machine, once. Move every value that can change out of the code. Use this order of precedence, strongest first:

1. **Command-line arguments** (this run only)
2. **Environment variables** (this machine or this scheduled job)
3. **A config file** (your normal settings)
4. **Defaults in the code** (safe, harmless ones)

`tomllib` (standard library since Python 3.11) reads TOML, the same format as `pyproject.toml`:

```python
# settings.py
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    inbox: Path
    backup_dir: Path
    keep_days: int
    api_token: str | None = field(default=None, repr=False)     # repr=False: never printed by accident


def load(path=None, env=None):
    env = os.environ if env is None else env
    data = {}
    if path and Path(path).exists():
        data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    return Settings(
        inbox=Path(env.get("AUTO_INBOX", data.get("inbox", "~/Downloads"))).expanduser(),
        backup_dir=Path(env.get("AUTO_BACKUP_DIR", data.get("backup_dir", "~/backups"))).expanduser(),
        keep_days=int(env.get("AUTO_KEEP_DAYS", data.get("keep_days", 14))),
        api_token=env.get("AUTO_API_TOKEN"),                      # secrets: environment only
    )
```

```python run
from pathlib import Path
import settings

Path("auto.toml").write_text('inbox = "~/Downloads"\nbackup_dir = "/data/backups"\nkeep_days = 30\n')
print("file only      :", settings.load("auto.toml", env={}))
print("env overrides  :", settings.load("auto.toml", env={"AUTO_KEEP_DAYS": "7", "AUTO_API_TOKEN": "s3cret"}))
print("no file at all :", settings.load("missing.toml", env={}).keep_days, "(the default)")
```
```text
file only      : Settings(inbox=PosixPath('/home/you/Downloads'), backup_dir=PosixPath('/data/backups'), keep_days=30)
env overrides  : Settings(inbox=PosixPath('/home/you/Downloads'), backup_dir=PosixPath('/data/backups'), keep_days=7)
no file at all : 14 (the default)
```

Notice the token is **not** shown in the output of the second line, because the dataclass hides it from `repr`. Rules for secrets:

- **Never** put passwords, tokens or API keys in the script, in the config file you commit, or on a command line (other users can see command lines with `ps`; shells keep history).
- Read them from environment variables, or from a file outside the repository with permissions only you can read (`chmod 600`), or from the operating system keyring (`pip install keyring`).
- A `.env` file is fine on your machine **if it is in `.gitignore`**; ship a `.env.example` with fake values.
- Do not log them. Do not print the whole `Settings` object in an error message unless secrets are hidden as above.

### 8.2 Logging that helps at 3 a.m.

A script that runs while you sleep must leave a trail. `print` is for the tool's output; **logging** is for the story of what happened. Use it from the start:

```python
# logsetup.py
import logging
import logging.handlers
import sys


def setup_logging(verbose=0, logfile=None, stream=None):
    level = logging.WARNING - 10 * min(verbose, 2)             # -v = INFO, -vv = DEBUG
    handlers = [logging.StreamHandler(stream or sys.stderr)]
    if logfile:
        handlers.append(logging.handlers.RotatingFileHandler(logfile, maxBytes=1_000_000, backupCount=3,
                                                             encoding="utf-8"))
    logging.basicConfig(level=level, handlers=handlers, force=True,
                        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s")
```

```python run
import logging
import os
import tempfile
from pathlib import Path

from logsetup import setup_logging

log = logging.getLogger("backup")
logfile = Path(tempfile.mkdtemp()) / "auto.log"
setup_logging(verbose=1, logfile=logfile, stream=open(os.devnull, "w"))   # hide the screen copy here
log.info("starting backup of %d folders", 3)
log.debug("this detail is hidden unless -vv")
log.warning("folder %s is empty", "photos")
try:
    1 / 0
except ZeroDivisionError:
    log.exception("backup step failed")                         # includes the traceback

lines = logfile.read_text().splitlines()
print(f"\nthe log file got {len(lines)} lines; the first three, without timestamps:")
for line in lines[:3]:
    print("  ", line.split(" ", 2)[2])
```
```text

the log file got 8 lines; the first three, without timestamps:
   INFO    backup: starting backup of 3 folders
   WARNING backup: folder photos is empty
   ERROR   backup: backup step failed
```

Why this setup: the screen gets messages on **stderr**, the file keeps history, `RotatingFileHandler` stops the log from filling the disk (swe.09 section 8), `-v` and `-vv` control detail, and `log.exception` records the traceback. Use `%s` placeholders instead of f-strings in log calls so the text is built only if the message is actually shown.

### Try it: where does this value go?

Decide: config file, environment variable, command-line argument or code constant: (a) the SMTP password; (b) the folder to tidy; (c) the number of days to keep backups; (d) a one-off `--dry-run`; (e) the list of file extensions per category.

<details><summary>Answer</summary>

(a) **environment variable** (or keyring): a secret. (b) **argument**, with a config default. (c) **config file**, overridable by env. (d) **argument**: it describes this run only. (e) **code constant** (or a config file if you really change it): it is part of the tool's behaviour, versioned with the code.

</details>

## 9. Data automation: from a CSV to a weekly e-mail

A very common weekly task: take an export, summarize it, send the summary. The standard library is enough. We separate three jobs so each can be tested: **summarize** (pure), **build the message** (pure), **send** (side effect, replaceable).

```python
# weekly.py
import csv
import io
from collections import defaultdict
from email.message import EmailMessage


def summarize(csv_text):
    """Total sales per region, from a CSV with columns region,amount. Bad rows are reported, not hidden."""
    totals, bad = defaultdict(float), []
    for line_no, row in enumerate(csv.DictReader(io.StringIO(csv_text)), start=2):   # line 1 is the header
        try:
            region = row["region"].strip()
            if not region:
                raise ValueError("missing region")
            amount = float(row["amount"])          # convert BEFORE touching totals: a failed row must leave no trace
            totals[region] += amount
        except (KeyError, ValueError, AttributeError):
            bad.append(line_no)
    return dict(sorted(totals.items())), bad


def build_email(totals, bad_lines, sender, to):
    lines = [f"{region:10} {amount:10,.2f}" for region, amount in totals.items()]
    lines.append(f"{'TOTAL':10} {sum(totals.values()):10,.2f}")
    if bad_lines:
        lines.append(f"\nWarning: could not read line(s) {bad_lines}. Please check the export.")
    msg = EmailMessage()
    msg["Subject"] = f"Weekly sales: {sum(totals.values()):,.2f}"
    msg["From"], msg["To"] = sender, to
    msg.set_content("\n".join(lines))
    return msg


class FakeTransport:
    """Stands in for smtplib. Tests and dry runs use this; production uses the real one."""
    def __init__(self):
        self.sent = []

    def send_message(self, msg):
        self.sent.append(msg)


def send(msg, transport):
    transport.send_message(msg)
```

```python run
from weekly import FakeTransport, build_email, send, summarize

export = """region,amount
north,1200.50
south,830
north,99.50
east,abc
west,410.25
,12
"""
totals, bad = summarize(export)
msg = build_email(totals, bad, "reports@example.com", "boss@example.com")
transport = FakeTransport()
send(msg, transport)
sent = transport.sent[0]
print("Subject:", sent["Subject"])
print("To     :", sent["To"])
print(sent.get_content())
```
```text
Subject: Weekly sales: 2,540.25
To     : boss@example.com
north        1,300.00
south          830.00
west           410.25
TOTAL        2,540.25

Warning: could not read line(s) [5, 7]. Please check the export.
```

Two choices worth copying. Bad rows are **reported** in the e-mail, not silently dropped (rule 4: fail loudly; a total that quietly ignores rows is a wrong total). And the sending is a parameter, so a test passes `FakeTransport` and no real e-mail leaves your machine.

The real sender is small. Read it, and try it on your machine with an account that allows it (many providers require an "app password" or an API instead of your normal one):

```python
# send_real.py  (needs a real mail account; do not run against addresses you do not own)
import os
import smtplib


def real_send(msg):
    with smtplib.SMTP_SSL(os.environ["SMTP_HOST"], 465, timeout=30) as smtp:
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])   # secrets from the environment
        smtp.send_message(msg)
```

Other data jobs follow the same shape: `json` for APIs, `sqlite3` for a local history, `openpyxl` (`pip install openpyxl`) to read and write `.xlsx` files, `pandas` for heavier tables (da.* modules). Keep the same three layers: read, transform (pure), write.

### Try it: test the bad-row rule

Write a test showing that a row with a non-numeric amount is listed in `bad` and not added to any total.

<details><summary>Answer</summary>

```python
def test_bad_rows_are_reported_not_hidden():
    totals, bad = summarize("region,amount\nnorth,10\neast,abc\n")
    assert totals == {"north": 10.0}
    assert bad == [3], "line 3 (counting the header as line 1) is unreadable"
```

</details>

## 10. Web automation without a browser

Before you reach for a browser robot, remember the **order of preference**:

1. **An official API.** Stable, fast, allowed. Check for one first.
2. **A hidden JSON endpoint** the website's own page uses (look in the browser's developer tools, Network tab). Quick, but unofficial and may change.
3. **Fetching the HTML** and parsing it. Works for pages whose content is in the HTML.
4. **A real browser** (section 11), only for pages that need JavaScript, logins or clicks.

The lower you go, the slower and more fragile it gets. To practise without hitting anyone's real website, we run a tiny local server with a page, a JSON endpoint and a `robots.txt`:

```python
# demo_server.py
import http.server
import json
import threading

PAGE = """<html><body><h1>Books</h1><ul>
<li class="book"><a href="/b/1">Python Basics</a> <span class="price">12.50</span></li>
<li class="book"><a href="/b/2">Automate It</a> <span class="price">20.00</span></li>
</ul></body></html>"""
ETAG = '"v1"'


class Handler(http.server.BaseHTTPRequestHandler):
    disable_nagle_algorithm = True

    def _send(self, status, body=b"", ctype="text/plain", headers=()):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in headers:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self._send(200, PAGE.encode(), "text/html")
        elif self.path == "/robots.txt":
            self._send(200, b"User-agent: *\nDisallow: /private\n")
        elif self.path == "/api/books":
            if self.headers.get("If-None-Match") == ETAG:
                self._send(304, headers=[("ETag", ETAG)])
            else:
                body = json.dumps([{"id": 1, "title": "Python Basics", "price": 12.5},
                                   {"id": 2, "title": "Automate It", "price": 20.0}]).encode()
                self._send(200, body, "application/json", [("ETag", ETAG)])
        else:
            self._send(404, b"not found")

    def log_message(self, *args):
        pass


def start():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"
```

### 10.1 Calling a JSON API well

`httpx` (installed; swe.02) is the modern client. A script that calls an API needs a **timeout**, a **status check**, and, when the data rarely changes, a **conditional request** so the server can answer "nothing new" (HTTP 304) and save both sides the transfer:

```python run
import httpx
from demo_server import start

server, base = start()
with httpx.Client(base_url=base, timeout=5.0, headers={"User-Agent": "my-automation/1.0 (me@example.com)"}) as client:
    r = client.get("/api/books")
    r.raise_for_status()                                          # 4xx/5xx -> exception, never ignored
    print("first call :", r.status_code, [b["title"] for b in r.json()], "| etag", r.headers["ETag"])

    r2 = client.get("/api/books", headers={"If-None-Match": r.headers["ETag"]})
    print("second call:", r2.status_code, "(Not Modified: use the copy you already have)")

    try:
        client.get("/missing").raise_for_status()
    except httpx.HTTPStatusError as e:
        print("error call :", e.response.status_code, "-> handled, not hidden")
server.shutdown()
```
```text
first call : 200 ['Python Basics', 'Automate It'] | etag "v1"
second call: 304 (Not Modified: use the copy you already have)
error call : 404 -> handled, not hidden
```

Set a **User-Agent** that says who you are and how to reach you. For rate-limited or flaky APIs add retries with backoff and jitter (swe.08, swe.10 section 12): `retry()` from swe.10 works unchanged.

### 10.2 Parsing HTML

The standard library's `html.parser` is enough for simple pages (for messy ones use `beautifulsoup4` or `lxml`, `pip install beautifulsoup4`). The idea is to **react to tags as they stream by**:

```python run
import httpx
from html.parser import HTMLParser

from demo_server import start


class BookParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.books, self._href, self._title, self._in_price = [], None, None, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href", "").startswith("/b/"):
            self._href = a["href"]
        elif tag == "span" and a.get("class") == "price":
            self._in_price = True

    def handle_data(self, data):
        if self._href:
            self._title = data.strip()
        elif self._in_price:
            self.books.append({"title": self._title, "url": self._last_href, "price": float(data)})
            self._in_price = False

    def handle_endtag(self, tag):
        if tag == "a" and self._href:
            self._last_href, self._href = self._href, None


server, base = start()
parser = BookParser()
parser.feed(httpx.get(base + "/", timeout=5).text)
for b in parser.books:
    print(b)
server.shutdown()
```
```text
{'title': 'Python Basics', 'url': '/b/1', 'price': 12.5}
{'title': 'Automate It', 'url': '/b/2', 'price': 20.0}
```

Scraping code is **fragile by nature**: the site changes its layout and your parser silently returns nothing. Defend yourself: assert that you found at least one item and raise a clear error if not, keep a saved copy of the page used in tests (a *fixture*), and log how many items you parsed each run so a sudden drop to zero alerts you.

### 10.3 Being a polite and legal automator

- **Read the terms of service.** Many sites forbid automated access; some allow it only through their API. Ignoring this can get your account or IP banned, or worse.
- **Check `robots.txt`**: it states which paths automated clients may visit. Python can read it:

```python run
import urllib.robotparser

import httpx
from demo_server import start

server, base = start()
rules = urllib.robotparser.RobotFileParser()
rules.parse(httpx.get(base + "/robots.txt", timeout=5).text.splitlines())
for path in ("/", "/api/books", "/private/data"):
    print(f"{path:16} allowed for my bot: {rules.can_fetch('my-automation', base + path)}")
server.shutdown()
```
```text
/                allowed for my bot: True
/api/books       allowed for my bot: True
/private/data    allowed for my bot: False
```

- **Rate limit yourself**: one request per second or slower unless told otherwise; never hammer a small site. Add `time.sleep` between requests and obey `Retry-After` headers.
- **Cache** what you fetched; do not download the same page twice in a day.
- **Do not collect personal data** you have no right to, and do not bypass logins, paywalls or CAPTCHAs.
- Prefer APIs and data exports: they exist precisely so you do not have to scrape.

### Try it: choose the level

You want today's exchange rate for your monthly invoice script. Choose among: scrape the bank's web page, call a public exchange-rate API, drive a browser to log into your bank. Explain.

<details><summary>Answer</summary>

The **public API** (level 1): stable, documented, fast, no login, allowed. Scraping a page (level 3) breaks when the layout changes; driving a browser into your bank (level 4) is slow, fragile, risks locking your account and may break the bank's terms. Go up the ladder only when the lower rung genuinely cannot do the job.

</details>

## 11. Browser automation with Playwright

### 11.1 When you need a real browser

Some pages build their content with JavaScript after loading, require clicking through a login, or show data only after interaction. A plain HTTP client sees an empty shell. A **browser automation** tool starts a real browser engine, loads the page, waits for it, clicks and types like a person, and lets you read the result. Use cases: filling a form you submit weekly, downloading a report behind a login, taking screenshots of a dashboard, and **testing your own web app end to end**.

**Playwright** (from Microsoft) is the current standard: it controls Chromium, Firefox and WebKit, **waits automatically** for elements to be ready (the main source of flaky scripts in older tools like Selenium), and has excellent tooling. It is not installed here and needs a browser download, so this section is a guided tutorial for your machine with no invented output.

### 11.2 Install and hello world

```bash
python -m venv .venv && source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install playwright
playwright install chromium                              # downloads a browser (a few hundred MB)
```

```python
# hello_playwright.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)           # headless = no visible window
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())                                   # prints the page title
    page.screenshot(path="example.png")
    browser.close()
```

**Try it on your machine:** run it. You should see the page title printed and an `example.png` file next to the script. Then change `headless=True` to `headless=False, slow_mo=500` and watch the browser work.

### 11.3 The practice target: our local page

Run the demo server from section 10 yourself (`python -c "import demo_server, time; s, url = demo_server.start(); print(url); time.sleep(600)"`) and point Playwright at it:

```python
# scrape_books.py   (needs playwright; run the demo server first and put its URL in BASE)
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:PORT"          # replace with the URL the server printed

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(BASE + "/")
    page.wait_for_selector("li.book")                                    # explicit wait for content
    for item in page.locator("li.book").all():
        title = item.locator("a").inner_text()
        price = float(item.locator(".price").inner_text())
        print(title, price)
    browser.close()
```

Expected result: the two books with their prices, matching section 10.2. (You compare it yourself; this book does not paste output it did not capture.)

### 11.4 The five ideas that make scripts robust

| Idea | In Playwright | Why |
|---|---|---|
| **Locators with auto-wait** | `page.locator("button")`, `page.get_by_role("button", name="Save")`, `page.get_by_label("Email")`, `page.get_by_text("Welcome")` | actions wait until the element is visible and enabled; no `sleep` |
| **Stable selectors** | prefer role, label, text or a `data-testid` over long CSS paths like `div > div:nth-child(3) > a` | layouts change; meanings change slowly |
| **Assertions with waiting** | `expect(page.get_by_text("Saved")).to_be_visible()` (from `playwright.sync_api import expect`) | retries until true or timeout |
| **Reuse the login** | log in once, `context.storage_state(path="auth.json")`, later `browser.new_context(storage_state="auth.json")` | you do not type the password on every run; protect `auth.json` like a password |
| **Evidence on failure** | `context.tracing.start(screenshots=True, snapshots=True)` then `stop(path="trace.zip")`, open with `playwright show-trace trace.zip` | you can replay exactly what happened |

A typical weekly job (login, download a report) looks like this; it is a template to adapt to a site you are **allowed** to automate:

```python
# download_report.py   (template; needs playwright and a site you are allowed to automate)
import os
from playwright.sync_api import expect, sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    page.set_default_timeout(15_000)                                       # 15 s, not the default forever-ish
    page.goto("https://reports.example.com/login")
    page.get_by_label("Email").fill(os.environ["REPORT_USER"])             # credentials from the environment
    page.get_by_label("Password").fill(os.environ["REPORT_PASSWORD"])
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_text("Dashboard")).to_be_visible()
    with page.expect_download() as download_info:                          # wait for the file
        page.get_by_role("link", name="Export CSV").click()
    download_info.value.save_as("weekly.csv")
    browser.close()
```

**Generate code by clicking:** `playwright codegen https://example.com` opens a browser and a window that writes the Python for what you click. It is the best way to learn the API; then clean up the generated selectors.

### 11.5 Browser automation traps

- **`time.sleep(5)` instead of waiting for something.** Too short is flaky; too long is slow. Wait for an element or a network event.
- **Selectors tied to layout.** One redesign and everything breaks.
- **CAPTCHAs and bot detection.** They exist to stop you. Do not try to defeat them; find an API or ask the site's owner.
- **Credentials in the script, or `auth.json` in git.**
- **Running headless on a server without the system libraries.** `playwright install --with-deps chromium` installs them on Linux.
- **Automating something the terms forbid** (section 10.3).
- **Using a browser when an API exists.** It is 100 times slower and breaks more.
- **No timeout.** A hung page freezes your scheduled job for ever (section 13).

### 11.6 Testing your own app with it

The most legitimate use of browser automation is testing *your* web app. With `pytest-playwright` (`pip install pytest-playwright`), a test receives a ready `page`:

```python
# test_home.py   (needs pytest-playwright and your app running locally)
from playwright.sync_api import Page, expect

def test_home_has_title(page: Page):
    page.goto("http://127.0.0.1:8000/")
    expect(page).to_have_title("Taskboard")
```

Keep such tests few (they are slow); test rules at the unit level as in swe.10 and use browser tests for the few journeys that matter (sign up, pay).

### Try it: wait for the right thing

A page loads a table after 2 seconds of JavaScript. Your script does `page.goto(url); rows = page.locator("tr").count()` and gets 0. Fix it without `sleep`.

<details><summary>Answer</summary>

Wait for the content, not for time: `page.wait_for_selector("tr.data-row")` first (or `expect(page.locator("tr.data-row").first).to_be_visible()`), then count. `locator.count()` does not wait; locator **actions** (`click`, `fill`, `inner_text`) do.

</details>

## 12. Scheduling: running scripts without you

### 12.1 cron

**cron** is the scheduler on Linux and macOS. You list jobs in a *crontab* with a five-field time pattern and a command:

```text
# minute  hour  day-of-month  month  day-of-week   command
  30      2     *             *      1-5           /home/me/venv/bin/python /home/me/tidy.py organize /home/me/Downloads >> /home/me/tidy.log 2>&1
```

| Field | Values | Special |
|---|---|---|
| minute | 0-59 | `*` any, `*/15` every 15, `1,31` a list, `10-20` a range |
| hour | 0-23 | |
| day of month | 1-31 | |
| month | 1-12 | |
| day of week | 0-6 (0 = Sunday; 7 also means Sunday on many systems) | |

Commands: `crontab -e` edits your jobs, `crontab -l` lists them, `crontab -r` **removes all of them** (there is no confirmation). Shortcuts like `@daily`, `@hourly`, `@reboot` exist too.

To make sure you understand a pattern *before* trusting it with a real job, here is a small implementation that answers "when will this run next?". It is also a nice exercise in parsing:

```python
# cronexpr.py
from datetime import datetime, timedelta

FIELDS = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]      # minute, hour, day of month, month, weekday (0 = Sunday)


def parse_field(text, lo, hi):
    values = set()
    for part in text.split(","):
        step = 1
        if "/" in part:
            part, step_text = part.split("/")
            step = int(step_text)
        if part == "*":
            a, b = lo, hi
        elif "-" in part:
            a, b = (int(x) for x in part.split("-"))
        else:
            a = int(part)
            b = hi if step > 1 else a
        if not (lo <= a <= b <= hi) or step < 1:
            raise ValueError(f"bad cron field {text!r}: allowed {lo}-{hi}")
        values.update(range(a, b + 1, step))
    return values


class Cron:
    def __init__(self, expression):
        parts = expression.split()
        if len(parts) != 5:
            raise ValueError("a cron expression has exactly 5 fields")
        self.sets = [parse_field(text, lo, hi) for text, (lo, hi) in zip(parts, FIELDS)]
        self.dom_star, self.dow_star = parts[2].startswith("*"), parts[4].startswith("*")

    def matches(self, dt):
        minute, hour, dom, month, dow = self.sets
        if dt.minute not in minute or dt.hour not in hour or dt.month not in month:
            return False
        dom_ok = dt.day in dom
        dow_ok = (dt.weekday() + 1) % 7 in dow                  # Python: Monday=0; cron: Sunday=0
        if self.dom_star or self.dow_star:
            return dom_ok and dow_ok
        return dom_ok or dow_ok                                  # the famous cron quirk: OR, not AND

    def next_runs(self, after, count=3, limit_days=800):
        t = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
        found, end = [], after + timedelta(days=limit_days)
        while t < end and len(found) < count:
            if self.matches(t):
                found.append(t)
            t += timedelta(minutes=1)
        return found
```

```python run
from datetime import datetime

from cronexpr import Cron

now = datetime(2026, 11, 9, 10, 7)
print("now:", now.strftime("%A %Y-%m-%d %H:%M"))
for expr in ["*/15 * * * *", "30 2 * * 1-5", "0 9 1 * *", "0 0 13 * 5"]:
    runs = Cron(expr).next_runs(now, 4)
    print(f"\n{expr}")
    for r in runs:
        print("   ", r.strftime("%a %Y-%m-%d %H:%M"))
try:
    Cron("61 * * * *")
except ValueError as e:
    print("\ninvalid:", e)
```
```text
now: Monday 2026-11-09 10:07

*/15 * * * *
    Mon 2026-11-09 10:15
    Mon 2026-11-09 10:30
    Mon 2026-11-09 10:45
    Mon 2026-11-09 11:00

30 2 * * 1-5
    Tue 2026-11-10 02:30
    Wed 2026-11-11 02:30
    Thu 2026-11-12 02:30
    Fri 2026-11-13 02:30

0 9 1 * *
    Tue 2026-12-01 09:00
    Fri 2027-01-01 09:00
    Mon 2027-02-01 09:00
    Mon 2027-03-01 09:00

0 0 13 * 5
    Fri 2026-11-13 00:00
    Fri 2026-11-20 00:00
    Fri 2026-11-27 00:00
    Fri 2026-12-04 00:00

invalid: bad cron field '61': allowed 0-59
```

Look at the last pattern: `0 0 13 * 5` is "midnight on the 13th **or** on any Friday", not "Friday the 13th". When *both* day fields are restricted, cron runs when *either* matches. Test patterns before you rely on them (online tools such as crontab.guru do the same).

### 12.2 Why a script works by hand and fails in cron

| Cause | What happens | Fix |
|---|---|---|
| **Tiny environment**: cron's `PATH` is `/usr/bin:/bin` | `python`, `git`, `node` not found | use **absolute paths** to every program, or set `PATH=` at the top of the crontab |
| **Different working directory** (your home, not the project) | relative paths point to the wrong place | use absolute paths; `Path(__file__).resolve().parent` |
| **Different Python**: system Python without your packages | `ModuleNotFoundError` | call the virtualenv's Python: `/home/me/venv/bin/python script.py` |
| **No terminal, no environment variables** from your shell profile | missing secrets and settings | set them in the crontab or a file the script reads |
| **Output vanishes** or is mailed to a local mailbox nobody reads | you never see the error | redirect `>> log 2>&1` (and log from Python, section 8) |
| **`%` in a crontab line** is a newline | `date +%F` breaks | escape as `\%` or put the command in a script |
| **Time zone and daylight saving** | job runs at an unexpected hour, twice or never on the change day | schedule in UTC or avoid 01:00-03:00; know the server's zone |
| **Machine off at the scheduled time** | the job is skipped | use `anacron` or a systemd timer with `Persistent=true`, or make the job catch up (section 13) |
| **Runs overlap**: a slow run is still going at the next tick | two copies fight over the same files | a lock (section 12.4), or `flock` |

A habit that removes most of these surprises: **run the exact cron command in a clean environment first**: `env -i /bin/sh -c '/home/me/venv/bin/python /home/me/tidy.py organize /tmp/x --dry-run'`.

### 12.3 Windows, systemd and Python schedulers

- **Windows Task Scheduler** is the cron of Windows. From a terminal, `schtasks /create /sc daily /st 08:00 /tn "Tidy downloads" /tr "C:\tools\venv\Scripts\python.exe C:\tools\tidy.py organize C:\Users\me\Downloads"` creates a daily 08:00 task; `schtasks /query /tn "Tidy downloads"` shows it and `schtasks /delete /tn "Tidy downloads" /f` removes it. In the graphical Task Scheduler you can also tick "Run task as soon as possible after a scheduled start is missed" (the catch-up cron lacks). Use the full path to `python.exe`, and set "Start in" to the script's folder.
- **systemd timers** (modern Linux) pair a `.service` (what to run) with a `.timer` (when). They log to the journal (`journalctl -u tidy`), can catch up after the machine was off (`Persistent=true`), and can prevent overlap. A timer for the same job:

```text
# ~/.config/systemd/user/tidy.service
[Service]
Type=oneshot
ExecStart=/home/me/venv/bin/python /home/me/tidy.py organize /home/me/Downloads

# ~/.config/systemd/user/tidy.timer
[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true
[Install]
WantedBy=timers.target
```

Enable with `systemctl --user enable --now tidy.timer`; list with `systemctl --user list-timers`. (Commands given for you to try; they change your machine, so this book does not run them.)

- **In-process schedulers** (`schedule`, `APScheduler`) run jobs inside a Python process that must stay alive. They are fine inside a long-running service you already operate (swe.08 section 14). For a personal script, the operating system's scheduler is more reliable: it starts the job fresh each time and survives your script crashing.

### 12.4 Never run two at once

If a job takes longer than its interval, or you start it by hand while cron also starts it, two copies run together. Add a **single-instance lock**. This version creates a lock file exclusively, stores the process id, and takes over a lock left behind by a crashed run:

```python
# onelock.py
import os
from contextlib import contextmanager

import psutil


class AlreadyRunning(Exception):
    pass


@contextmanager
def single_instance(path):
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)           # fails if the file exists
    except FileExistsError:
        try:
            pid = int(open(path).read().strip())
        except ValueError:
            pid = None
        if pid and psutil.pid_exists(pid):
            raise AlreadyRunning(f"already running as process {pid}")
        os.unlink(path)                                                     # stale lock from a crashed run
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
```

```python run
import os
import tempfile
from pathlib import Path

from onelock import AlreadyRunning, single_instance

lock = Path(tempfile.mkdtemp()) / "job.lock"
with single_instance(lock):
    print("first copy running, lock file exists:", lock.exists())
    try:
        with single_instance(lock):
            print("second copy started (BUG)")
    except AlreadyRunning as e:
        print("second copy refused:", e)
print("after finishing, lock file exists:", lock.exists())   # (the process id above differs on every run)

lock.write_text("99999999")                                  # a pid that does not exist = a crashed run
with single_instance(lock):
    print("stale lock taken over")
```
```text
first copy running, lock file exists: True
second copy refused: already running as process 120615
after finishing, lock file exists: False
stale lock taken over
```

On Linux and macOS the shell tool `flock` does the same without code: `flock -n /tmp/job.lock python job.py` (exit immediately if locked). This pure-Python version also works on Windows. (A rare race remains if two processes take over a stale lock at the very same instant; for stricter needs use a library such as `portalocker`, or a database row.)

### Try it: read a crontab line

Say in words when each runs: (a) `0 */6 * * *`; (b) `15 3 * * 0`; (c) `*/5 9-17 * * 1-5`.

<details><summary>Answer</summary>

(a) At minute 0 of every 6th hour: 00:00, 06:00, 12:00, 18:00 daily. (b) 03:15 every Sunday. (c) Every 5 minutes between 09:00 and 17:55, Monday to Friday. Check yourself with `Cron(expr).next_runs(...)` from above.

</details>

## 13. Making scheduled jobs reliable

An unattended job fails in the most boring ways: the network is down, the disk is full, the site changed, a password expired. The danger is not the failure but that **nobody notices**. Add four habits.

### 13.1 One wrapper that records every run

A tiny runner executes a job, logs it, measures the time, and writes a **status file** (atomically, section 6.3) that something else can inspect:

```python
# jobrunner.py
import json
import logging
import os
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

log = logging.getLogger("job")


def write_json_atomic(path, data):
    fd, tmp = tempfile.mkstemp(dir=Path(path).parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(tmp, path)


def run_job(name, fn, status_dir):
    """Run fn(), always record the outcome, return an exit code (0 ok, 1 failed)."""
    Path(status_dir).mkdir(parents=True, exist_ok=True)
    started, begin = datetime.now(timezone.utc), time.monotonic()
    status = {"job": name, "started": started.isoformat()}
    log.info("job %s starting", name)
    try:
        status.update(ok=True, result=fn())
        code = 0
    except Exception as e:
        log.error("job %s failed: %s", name, e)
        log.debug("traceback", exc_info=True)                 # shown with -vv
        status.update(ok=False, error=f"{type(e).__name__}: {e}")
        code = 1
    status["seconds"] = round(time.monotonic() - begin, 3)
    write_json_atomic(Path(status_dir) / f"{name}.json", status)
    log.info("job %s finished: ok=%s in %.3fs", name, status["ok"], status["seconds"])
    return code


def problem_with(status_file, max_age_hours, now=None):
    """Return a string describing what is wrong with a job, or None if it looks healthy."""
    now = now or datetime.now(timezone.utc)
    path = Path(status_file)
    if not path.exists():
        return "never ran"
    status = json.loads(path.read_text(encoding="utf-8"))
    if not status["ok"]:
        return f"last run failed: {status['error']}"
    age = now - datetime.fromisoformat(status["started"])
    if age > timedelta(hours=max_age_hours):
        return f"last success was {age.total_seconds() / 3600:.0f} hours ago (limit {max_age_hours})"
    return None
```

```python run
import logging
import sys
import tempfile
from datetime import datetime, timedelta, timezone

from jobrunner import problem_with, run_job

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s %(message)s")
status_dir = tempfile.mkdtemp()


def good():
    return {"files_moved": 12}


def bad():
    raise ConnectionError("backup server unreachable")


print("exit codes:", run_job("tidy", good, status_dir), run_job("backup", bad, status_dir))
print()
for name in ("tidy", "backup", "report"):
    print(f"{name:8} problem: {problem_with(f'{status_dir}/{name}.json', max_age_hours=24)}")

in_two_days = datetime.now(timezone.utc) + timedelta(days=2)
print("tidy two days later:", problem_with(f"{status_dir}/tidy.json", 24, now=in_two_days))
```
```text
INFO job tidy starting
INFO job tidy finished: ok=True in 0.000s
INFO job backup starting
ERROR job backup failed: backup server unreachable
INFO job backup finished: ok=False in 0.000s
exit codes: 0 1

tidy     problem: None
backup   problem: last run failed: ConnectionError: backup server unreachable
report   problem: never ran
tidy two days later: last success was 48 hours ago (limit 24)
```

The last check is the key idea: a job can also fail by **not running at all** (cron stopped, machine off, crontab lost). A status file with a timestamp lets a separate check say "no success in 24 hours".

### 13.2 Get told: alerts and the dead-man's switch

- Send yourself a message on failure: e-mail (section 9), a chat webhook, or a push service. Keep it short: job name, error, where the log is.
- Alert on **silence**, not just errors. A *dead-man's switch* (heartbeat) service such as Healthchecks.io gives each job a URL; the job requests it on success (`httpx.get(url, timeout=10)`), and the service alerts you if the ping does *not* arrive on time. This catches the failures that cannot report themselves, such as a dead machine.
- Make the exit code truthful, so the scheduler, CI and monitoring see failures.

### 13.3 Idempotent jobs and catching up

Write jobs so that running them again, late, or twice is harmless:

- **Key the work by date or id**, not by "now": "report for week 45" can be rebuilt any time; "report for whenever I ran" cannot.
- **Record progress** (last processed id, last date) in a small state file written atomically; start from there. Then a missed run is repaired by the next run.
- **Write results to a temporary name and rename** (section 6.3), so a crash leaves no half result.
- **Make deletion and sending the last steps**, after the result is safely stored.

### 13.4 Retries, timeouts and limits

- Every network call has a timeout; every subprocess has a timeout (section 7).
- Retry transient failures a few times with backoff and jitter; do not retry forever (swe.10 section 12).
- Cap the whole job's runtime (`timeout 600 python job.py` in cron, or a watchdog inside the script) so one hung run cannot block all later runs.

### Try it: what is missing?

A nightly backup job exits 0 even when the copy failed, because the script catches the exception and prints "oops". List what is wrong and three fixes.

<details><summary>Answer</summary>

It breaks rule 4 (fail loudly): the scheduler and any monitor see success. Fixes: log with `log.exception` and **return a non-zero exit code**; write a status file and check its age; alert on failure and on silence (dead-man's switch). Catch only the errors you can handle, and let the rest stop the job.

</details>

## 14. Packaging and sharing your tools

A script that lives in `~/scripts/tidy.py` is hard to run from anywhere. A few small steps turn it into a command:

1. **Use a virtual environment** per project, and call its Python from cron: `/home/me/automation/.venv/bin/python`.
2. **Declare it as a command** in `pyproject.toml`; after `pip install -e .` the name `tidy` works in any folder:

```text
# pyproject.toml
[project]
name = "automation"
version = "1.0"
requires-python = ">=3.11"
dependencies = ["click>=8"]

[project.scripts]
tidy = "tidy_click:cli"
auto = "auto:main"
```

3. **`pipx install .`** installs a tool in its own isolated environment and puts the command on your PATH. This is the clean way to install tools you use daily.
4. On Linux and macOS a script can start with `#!/usr/bin/env python3` and be made executable with `chmod +x`; on Windows use the `py` launcher (`py tidy.py ...`) or a `.bat` file.
5. Pin versions (`requirements.txt` or a lock file) so a library update cannot silently break the Monday job (swe.09).
6. Put the tools in **git**, with a README that shows the three commands you actually use. Future you is the other developer.

### Try it on your machine

In a new folder with `tidylib.py` and `tidy_click.py` from section 5, create the `pyproject.toml` above (without the `auto` line), run `python -m venv .venv`, activate it, `pip install -e .`, and then run `tidy --help` from a different folder. If it works from anywhere, the packaging works.

## 15. Structuring a personal automation suite

After a few scripts you will have a folder of unrelated files, each with its own argument parsing, logging and config. Give the collection a shape. This is the same lesson as swe.10 at small scale: pull out what repeats.

```text
automation/
  pyproject.toml
  auto.toml.example            settings template (real auto.toml is git-ignored)
  auto/
    __init__.py
    cli.py                     the `auto` command: subcommands only, thin
    settings.py                section 8: load config + env
    logsetup.py                section 8: logging
    jobrunner.py               section 13: status files, exit codes
    tasks/
      tidy.py                  logic + small functions (section 3)
      weekly_report.py         (section 9)
      disk_check.py            health checks
      backup.py
  tests/
    test_tidy.py ...
  docs/
    README.md                  what each task does, how it is scheduled
```

Rules for the shape:

- **One command, many tasks**: `auto tidy`, `auto report`, `auto check-disk`. One place for `--dry-run`, `-v` and `--config`.
- **Each task is a plain function** that takes settings and returns a result or raises. Tasks do not parse arguments or configure logging.
- **The runner wraps every scheduled task** (section 13), so each leaves a status file and an honest exit code.
- **Tests per task** with `tmp_path` and fakes (sections 4 and 9).
- **A README table**: task, what it changes, how often, how to run safely (`--dry-run`), how to undo.

A registry makes adding a task one function, as in this skeleton (the `disk-check` task from section 7 is a real example):

```python
# auto_demo.py
import argparse
import shutil
import sys

TASKS = {}


def task(name):
    def register(fn):
        TASKS[name] = fn
        return fn
    return register


@task("check-disk")
def check_disk(args):
    total, used, free = shutil.disk_usage(args.path)
    free_pct = free / total * 100
    print(f"{args.path}: {free_pct:.0f}% free")
    return 0 if free_pct >= args.min_free else 1          # non-zero exit = the alarm


@task("hello")
def hello(args):
    print("hello from a registered task")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="auto")
    p.add_argument("task", choices=sorted(TASKS))
    p.add_argument("--path", default="/")
    p.add_argument("--min-free", type=float, default=10.0, help="alarm below this percentage")
    args = p.parse_args(argv)
    return TASKS[args.task](args)


if __name__ == "__main__":
    sys.exit(main())
```

```bash run
python auto_demo.py --help
python auto_demo.py hello
python auto_demo.py check-disk --min-free 1; echo "exit code: $?"
python auto_demo.py check-disk --min-free 99.9; echo "exit code: $?"
```
```text
usage: auto [-h] [--path PATH] [--min-free MIN_FREE] {check-disk,hello}

positional arguments:
  {check-disk,hello}

options:
  -h, --help           show this help message and exit
  --path PATH
  --min-free MIN_FREE  alarm below this percentage
hello from a registered task
/: 23% free
exit code: 0
/: 23% free
exit code: 1
```

The last command pretends the disk is almost full, so it exits with 1: exactly what a scheduled monitor wants. Nothing in the task knows about cron; it just tells the truth through its exit code.

## 16. Project: your personal automation suite

### 16.1 The task

Build a small suite of **three tools** under one command, each automating something you really do (use the winner of the exercise in section 1). One must be file or system work, one must work with data or the web, and one must run on a schedule.

### 16.2 Requirements

1. **Structure** as in section 15: a package, a thin CLI, tasks as functions, tests, a README table.
2. **Safety**: every task that changes anything has `--dry-run`, never overwrites, and either can be undone (journal) or only moves to a trash folder.
3. **Config and secrets**: settings from a TOML file with environment overrides; secrets only from the environment; a `.example` file committed, the real one ignored.
4. **Logging**: `-v` flags, a rotating log file, tracebacks logged; honest exit codes.
5. **Tests**: at least 12 tests with `tmp_path` and fakes. Include a test for each safety rule (dry run changes nothing; second run is harmless; nothing is overwritten).
6. **Scheduling**: one task scheduled with cron, Task Scheduler or a systemd timer, using absolute paths and a single-instance lock; the job writes a status file, and `problem_with` (section 13) reports on it.
7. **Documentation**: a README describing each task (what it changes, how often, how to run safely, how to undo) and the exact scheduler line you installed.

### 16.3 Acceptance checklist

| Check | Done when |
|---|---|
| Real use | You ran at least one task on real data and it saved you time |
| Look before leaping | `--dry-run` output matches what the real run does |
| Safe twice | Running a task twice in a row produces no extra changes |
| Reversible | You demonstrated an undo, or showed the trash folder |
| Fails loudly | You broke a dependency on purpose; the exit code was non-zero and the log says why |
| Unattended | The scheduled job ran at least twice without you; the status file proves it |
| Silence detected | You stopped the job on purpose and `problem_with` reported it |
| No secrets in git | `git log -p` shows none; `.gitignore` covers config and logs |

### 16.4 Stretch goals

- Add a notification (chat webhook or e-mail) on failure and a dead-man's-switch ping on success.
- Replace the CLI with Typer, keeping the task functions untouched; note how many lines changed.
- Automate a web task with Playwright **on a site you are allowed to use**, with stored login state and a trace on failure.
- Run the suite on a second operating system (or inside a Docker container) and fix the assumptions that break (path separators, absolute paths, Python location).

### 16.5 Questions for your README

1. How many minutes per year does each task save, and how long did it take to build?
2. Which safety rule saved you from a mistake during development?
3. What is the worst thing that happens if a task runs on the wrong folder, and what prevents it?
4. What will break first in six months, and how will you find out?

## 17. Common traps

1. **No dry run, no undo**: a script that moves or deletes straight away (1.3, 3).
2. **Overwriting** an existing file silently with `move`, `copy` or `write` (3, 6.2).
3. **Hard-coded paths and secrets** in the script (8).
4. **`shell=True` with text you did not write**: shell injection (7.1).
5. **Subprocesses and network calls with no timeout** (7.1, 10.1, 13.4).
6. **Logic at import time** instead of in `main()`, so tests and imports run the job (2.2).
7. **`print` for everything**: progress mixed into data on stdout; no log file (2.4, 8.2).
8. **Exit code 0 on failure** because an exception was caught and printed (2.3, 13).
9. **Deleting by string-built paths** or following symlinks; no check that the target is inside the intended folder (6.4).
10. **Half-written output files** after a crash; no atomic write (6.3).
11. **Relative paths and `~` in cron**; assuming cron has your PATH, working directory or Python (12.2).
12. **Overlapping runs** with no lock (12.4).
13. **Believing a job works because it ran once by hand**; never testing the exact cron command in a clean environment (12.2).
14. **No alert on silence**: the job stopped weeks ago and nobody noticed (13).
15. **Non-idempotent jobs**: a re-run sends the e-mail twice or duplicates rows (13.3).
16. **Scraping when an API exists**, ignoring `robots.txt` and terms of service, or hammering a small site (10, 10.3).
17. **Fixed `sleep` in browser scripts** instead of waiting for elements; layout-based selectors (11.4, 11.5).
18. **Committing `auth.json`, `.env` or config with credentials** (8.1, 11.4).
19. **Over-engineering**: a framework for a ten-line task, or an automation that takes longer to maintain than the task takes to do (1.1).
20. **Automating a task that needs human judgement** without a review step (1.2).

## 18. Collected traps

| If you see... | The cause is usually... | Look at |
|---|---|---|
| A file vanished after the script ran | overwritten by a move/copy with the same name | 3, 6.2 |
| `command not found` only in cron | cron's minimal `PATH` | 12.2 |
| `ModuleNotFoundError` only in cron | wrong Python; not the venv's | 12.2 |
| The script cannot find its data file in cron | relative path; different working directory | 6.2, 12.2 |
| `date +%F` breaks in a crontab | unescaped `%` | 12.2 |
| The job runs an hour off, or twice, in spring/autumn | daylight saving time | 12.2 |
| Two copies fight over the same files | no single-instance lock | 12.4 |
| A job ran fine for months and silently stopped | no alert on silence | 13.2 |
| Scheduler says success but nothing was done | exit code 0 after a caught error | 2.3, 13 |
| A truncated JSON/CSV broke the next run | non-atomic write | 6.3 |
| Strange first line when piping output to `sort` | diagnostics printed to stdout | 2.4 |
| A filename with `;` or spaces ran a command | `shell=True` with built strings | 7.1 |
| The script hangs for ever | no timeout on a network call or subprocess | 7.1, 13.4 |
| `argparse` shows "invalid choice" for a command | typo; exit code 2 is normal | 3 |
| Scraper returns an empty list after a site redesign | fragile selectors, no "found nothing" check | 10.2 |
| Browser script works sometimes | `sleep` instead of auto-waiting | 11.4 |
| 403 or a ban from a website | ignoring robots.txt/terms/rate limits | 10.3 |
| Password appeared in `ps` or shell history | secret passed as an argument | 8.1 |
| The disk filled with logs | no rotation | 8.2 |
| Report totals look too small | bad rows silently dropped | 9 |

## 19. Summary

- **Automation pays when** (minutes per run × runs per year) clearly exceeds the cost of building and maintaining it. Climb the levels only as far as needed: checklist, one-liner, script, CLI tool, scheduled job.
- **Four rules of safe automation**: look before you leap (`--dry-run`), be able to undo (journal or trash), be safe to run twice (idempotent), fail loudly (honest exit codes).
- **A good script** has `main(argv)`, logic in testable functions, `pathlib` paths, `logging` for the story and stdout only for data, and returns an exit code through `sys.exit(main())`.
- **CLI libraries**: `argparse` (no dependency, subcommands, exit code 2 on misuse), **Click** (decorators, prompts, test runner), **Typer** (type hints), **rich** (readable output that degrades when piped). Keep the logic out of the CLI layer; the CLI should be thin.
- **Testing** CLI tools with `tmp_path`, `capsys`, `main(argv)` and Click's `CliRunner`; give every safety rule its own test.
- **File automation**: plan separately from doing; never overwrite; write atomically (temp file then `os.replace`); prefer moving to a trash over deleting; check that targets stay inside the intended folder; hash in chunks and compare sizes first.
- **`subprocess`**: argument lists, `check=True`, `capture_output`, `timeout`, never `shell=True` with untrusted text.
- **Config and secrets**: precedence of argument, environment, file, default; secrets only from the environment or a keyring, never in code, logs or command lines; rotating logs with `-v` levels.
- **Data jobs** split into read, transform (pure) and send (replaceable); report bad rows instead of hiding them.
- **Web automation ladder**: API, hidden JSON endpoint, HTML parsing, real browser. Use timeouts, conditional requests, an honest User-Agent, `robots.txt`, rate limits and the terms of service. **Playwright** adds auto-waiting locators, stored login state and traces; avoid `sleep` and layout-based selectors.
- **Scheduling**: cron's five fields (and its day-OR quirk), the traps of cron's tiny environment (absolute paths, the right Python, no `%`), Windows Task Scheduler, systemd timers, and a single-instance lock.
- **Reliability**: a runner that records every run in a status file, alerts on failure and on silence, idempotent jobs keyed by date, retries with limits and timeouts.
- **Structure** a suite as one thin command, task functions, shared settings/logging/runner, tests and a README table; package with `pyproject.toml` scripts and install with `pipx`.

Next: the 30 problems for this module practise reading and fixing scripts, tracing what a dry run and a real run do, predicting argparse and cron behaviour, spotting unsafe file and subprocess code, writing tests for tools, parsing HTML and cron patterns, and building small safe automations; the project is your own personal automation suite.
