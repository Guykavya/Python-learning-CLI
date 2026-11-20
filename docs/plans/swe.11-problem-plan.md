# Problem plan: swe.11 Automation and scripting (30 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`main(argv)` returning an exit code for CLI problems). Ids `swe.11.p001`…`p030`.

**Mix:** 12 drill, 10 applied, 6 deep, 2 challenge. **Kinds:** 23 code, 4 trace, 3 explain.
**assessment:** explain = p011, trace = p009, fix = p016, build = p030.
**★ core set:** p003, p004, p006, p007, p009, p011, p016, p018, p021, p026, p027, p030 (outcome: automate a task you really do every week, safely and repeatably).

**Testing notes**
- **Libraries:** standard library + `click` (a dependency of Flask, always present). **Typer, rich and Playwright are not used** in any test: Typer and Playwright are not declared in `pyproject.toml` (Typer happens to be importable on this machine only as a side effect), and the chapter treats them as "Try it on your machine". A browser is never assumed.
- CLI problems expose `main(argv: list[str] | None = None) -> int` (Ch. 2.2); tests call it directly with `capsys`, and Click problems use `click.testing.CliRunner`. One test per tool also runs it as a real child process with `sys.executable` to check the exit code end to end.
- **All file work happens in `tmp_path`** (the chapter's `messy` fixture, Ch. 4). Times are injected (`now=`), never read from the clock, so "older than 30 days" is exact; file times set with `os.utime`.
- No real cron, Task Scheduler or systemd: scheduling problems work on crontab text and on the run wrapper's status files.
- Web automation (p022) talks to a local `http.server` on `127.0.0.1` port 0 started by the test (Ch. 10.2's practice page).
- E-mail is never sent: the chapter's `FakeTransport` (Ch. 9) records messages.

## A. What is worth automating, and script anatomy (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Is it worth it? | drill | code | `worth_it(minutes_per_run, runs_per_year, minutes_to_build, minutes_to_maintain_per_year, years=3)` (Ch. 1.1) → `(worth, minutes_saved)`; break-even case; zero runs |
| 2 | What is wrong with this script? | drill | explain | the chapter's first script (Ch. 2.1): hard-coded path, no dry run, `print` for errors, exit 0 on failure, works only from one folder; say what goes wrong for each and the fix (Ch. "Try it: what is wrong?") |
| 3 | Exit codes and the two streams | drill | code | `main(argv)`: data to stdout, messages to stderr, 0 success, 1 runtime failure (missing folder), 2 usage error; `python tool.py ... | wc -l` must count only data lines (test checks `capsys` out/err separately) (Ch. 2.3–2.4) |

## B. A real tool with argparse: `tidy` (Ch. 3–4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 4 | The `tidy` parser | drill | code | `build_parser()` with subcommands `organize FOLDER [--dry-run]`, `undo FOLDER`, `dupes FOLDER [--min-size N]`, a global `-v` count; `--help` exits 0; a missing subcommand exits 2 |
| 5 | Where does each file go? | drill | code | `category_for(path)` (case-insensitive extension map, default `other`) and `unique_destination(dst)` → `a (1).txt`, `a (2).txt`; never returns an existing path |
| 6 | Plan, then move, with a dry run | applied | code | `plan_moves(root)` skips hidden files and the category folders; `apply_moves(moves, root, dry_run)` writes a JSON undo log; dry run changes nothing on disk (the test snapshots the tree) |
| 7 | Twice is harmless, undo is exact | applied | code | running `organize` twice moves nothing the second time; `undo(root)` restores every file to its original path and removes the log; the chapter's tests of Ch. 4 adapted (Ch. "Try it: the test that proves it") |
| 8 | Find duplicates by content | deep | code | `find_duplicates(root, min_size)`: group by size first, then SHA-256 in chunks; names do not matter; empty files ignored by default; results sorted for a stable answer |
| 9 | What does argparse make of it? | drill | trace | `assessment = "trace"`. `⚠ HAND-TRACE` 6 command lines against the `tidy` parser (`-vv organize x`, `organize --dry-run`, `dupes x --min-size abc`, …); write the resulting `Namespace` fields or `exit 2`; confirm by running when writing |

## C. Click (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 10 | The same tool in Click | applied | code | `cli` group with `organize` and `undo` commands, `click.Path(exists=True, file_okay=False)`, `--dry-run` flag; calls the **same** functions as the argparse version; tested with `CliRunner` (exit codes, output) |
| 11 | Keep the command line thin | applied | explain | `assessment = "explain"`. Why the logic lives in plain functions and the CLI layer only parses and prints: testing without a terminal, two front ends (argparse and Click) for one core, reuse in a scheduled job (Ch. 5.4, "Try it: spot the thin layer"); checklist |

## D. Files and folders (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 12 | Write a file so a crash cannot break it | drill | code | `atomic_write_text(path, text)` via a temp file in the same folder, `flush` + `os.fsync`, `os.replace`; a simulated crash before replace leaves the old content (Ch. 6.3) |
| 13 | Delete old files, safely | deep | code | `delete_older_than(root, days, now, dry_run=True)`: only regular files inside `root` (`is_inside`, Ch. 6.4), never follows symlinks out of the folder, dry run by default, returns what it would delete; a `root` of `/` or the home folder is refused |
| 14 | What changed since last time? | applied | code | `snapshot(root)` → `{relpath: (size, mtime_ns)}`; `changes(old, new)` → added, removed, modified, sorted (Ch. 6.5) |
| 15 | Path traps | drill | trace | `⚠ HAND-TRACE` 6 `pathlib` expressions (`Path("data") / "/etc"`, `.suffix` of `"a.tar.gz"`, `.stem`, `glob("*")` with a hidden file, `with_suffix("")`, `resolve()` of `..`); write each result (Ch. 6.2) |

## E. Running other programs (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 16 | Fix the injection | applied | code | `assessment = "fix"`. `count_lines(filename)` builds `subprocess.run(f"... {filename}", shell=True)`; a file named `x; echo HACKED` runs a second command. Fix with a list of arguments (child is `sys.executable -c ...`), no shell; tests with spaces, quotes and `;` in names (Ch. 7.1, "Try it: fix the injection") |
| 17 | Run with a timeout and a useful error | deep | code | `run_tool(args, timeout)`: `capture_output`, `text=True`, `check=True`; a timeout or a non-zero exit becomes `ToolFailed` with the command, the code and the **last 5 lines** of stderr; the child is a small Python script that sleeps or fails |

## F. Configuration and logging (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 18 | Defaults, file, environment, flags | applied | code | the chapter's `load(path=None, env=None)` (Ch. 8.1) extended with CLI overrides: defaults < TOML file (`tomllib`) < environment `TIDY_*` < flags; types converted; unknown keys in the file reported |
| 19 | Where does this value go? | drill | trace | `⚠ HAND-TRACE` 5 settings given in different places; write the final value of each and its source (Ch. "Try it: where does this value go?") |
| 20 | Logging that helps at 3 a.m. | drill | code | `setup_logging(verbose, logfile, stream)` (Ch. 8.2): console WARNING/INFO/DEBUG by `-v` count, the log file always DEBUG with timestamps, no duplicate handlers when called twice |

## G. Data and web automation (Ch. 9–11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 21 | From a CSV to a weekly e-mail | applied | code | `summarize(csv_text)` → totals per category and **bad rows reported, not hidden** (line numbers); `build_email(totals, bad_lines, sender, to)` with `email.message.EmailMessage`; `send(msg, transport)` with the fake (Ch. 9, "Try it: test the bad-row rule") |
| 22 | Web automation without a browser | applied | code | against the test's local server: `fetch_books(base_url)` with a timeout, follows the "next page" links, parses titles and prices with `html.parser` (the chapter's `BookParser` style); a 500 page raises with the URL |
| 23 | Wait for the right thing | deep | explain | browser automation (Playwright, read-only here): why `sleep(3)` is flaky, what to wait for instead (an element state, a network response), why text locators beat CSS paths (Ch. 11.4–11.5, "Try it: wait for the right thing") |

## H. Scheduling and reliable jobs (Ch. 12–13)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 24 | Read a crontab line | drill | trace | `⚠ HAND-TRACE` 5 crontab lines (`*/15 * * * *`, `0 9 * * 1-5`, `30 2 1 * *`, `@reboot`, a line with `%`); write in words when each runs and one problem with the last (Ch. "Try it: read a crontab line") |
| 25 | A crontab line that works under cron | drill | code | `cron_line(schedule, python, script, log)`: absolute interpreter and script paths, `cd` to the project, both streams appended to the log (`>> log 2>&1`), `%` escaped; relative paths raise `ValueError` (Ch. 12.2) |
| 26 | Never run two at once | deep | code | `single_instance(lock_path)` context manager (Ch. 12.4): creates the lock with `O_CREAT | O_EXCL`, writes the pid, raises `AlreadyRunning`; a stale lock whose pid is not alive is taken over; the lock is removed on exit even after an exception |
| 27 | Record every run, and notice silence | deep | code | `run_job(name, fn, status_dir, now)` writes `{name}.json` atomically with start, end, ok, error (Ch. 13.1); `problem_with(status_file, max_age_hours, now)` → `None`, `"failed"`, `"stale"` (dead-man's switch, Ch. 13.2) |
| 28 | Catch up after downtime | challenge | code | `missed_days(last_success, now)` and `run_daily(job, state_path, now)`: runs each missed day once, in order, idempotently (a day already done is skipped), stops at the first failure and resumes from it next time (Ch. 13.3–13.4) |

## I. The suite (Ch. 14–16)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 29 | A task registry | applied | code | `@task("name")` decorator filling a registry; `main(argv)` with `list`, `run NAME [args]`; unknown task → exit 2 with the list; each task wrapped by p027's `run_job` (Ch. 15, the chapter's `task(name)`/`check_disk`/`hello`) |
| 30 | Your personal automation suite | challenge | code | `assessment = "build"`. `auto` with three tasks: `tidy` (organize with dry run and undo), `report` (CSV → e-mail through a transport), `cleanup` (old files, dry run by default); shared settings (file + env + flags), logging, single instance, status files. Tests: each task end to end in `tmp_path`, dry runs change nothing, a second instance exits with code 3, a failing task leaves a `failed` status and exit 1, `--help` lists the tasks |

## Counts check

Tiers: drill 1, 2, 3, 4, 5, 9, 12, 15, 19, 20, 24, 25 (12); applied 6, 7, 10, 11, 14, 16, 18, 21, 22, 29 (10); deep 8, 13, 17, 23, 26, 27 (6); challenge 28, 30 (2). Total 30.
Kinds: trace 9, 15, 19, 24 (4); explain 2, 11, 23 (3); code 23.

## Risks and open questions

- p026: `os.kill(pid, 0)` to test "is the pid alive" does not work the same on Windows; the reference uses a small `pid_alive(pid)` helper with a Windows branch (`OpenProcess` via `ctypes`), or the test injects `is_alive`. Prefer injecting it.
- p013: creating symlinks in tests needs privileges on Windows; the symlink test is skipped there with `pytest.mark.skipif(os.name == "nt")`, and the other tests still run.
- p022's local server must serve the pages from strings in the test (no `.html` fixture files needed, R1).
