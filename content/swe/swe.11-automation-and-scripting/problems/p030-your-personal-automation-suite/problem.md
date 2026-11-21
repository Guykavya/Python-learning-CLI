# Your personal automation suite

Chapter sections 15 (structuring a personal automation suite) and 16 (project), using almost every earlier section. This is the module's outcome: **automate a task you really do every week, safely and repeatably**. Build `auto`, one command with three tasks, where every run is safe to try (dry runs), configurable (file, environment, flags), logged, protected against running twice, and recorded in a status file with an honest exit code.

You have written every piece already (p006/p007 tidy, p013 cleanup, p018 settings, p020 logging, p021 report, p026 lock, p027 runner). The starter gives the small helpers (`CATEGORIES`, `category_for`, `unique_destination`, `JOURNAL`, `write_json_atomic`, `FakeTransport`, `AlreadyRunning`, `pid_alive`); copy and adapt your own solutions for the rest.

## The command line

```text
auto [--config FILE] [--status-dir DIR] [-v] COMMAND ...
  tidy FOLDER [-n/--dry-run] [--undo]          sort FOLDER into subfolders by type; --undo reverses the last tidy
  report CSVFILE [--to ADDR] [-n/--dry-run]    summarize a region,amount CSV and e-mail it
  cleanup FOLDER [--days N] [--yes]            delete files older than N days; a dry run unless --yes
```

```python
def main(argv=None, env=None, transport=None, now=None) -> int: ...
```

`env` is the environment (`None` means `os.environ`), `transport` the mail transport (`None` means none configured), `now` the current time as an aware `datetime` (`None` means the real clock). The tests always pass `env`, and pass `transport` and `now` when they need them.

## The rules

**Settings** (a plain dict is fine), weakest first: defaults < TOML file from `--config` < environment `AUTO_*` < flags.

| Key | Default | Environment | Flag |
|---|---|---|---|
| `status_dir` | `"auto-status"` | `AUTO_STATUS_DIR` | `--status-dir` |
| `keep_days` | `30` (an `int`) | `AUTO_KEEP_DAYS` | `cleanup --days` |
| `sender` | `"auto@localhost"` | `AUTO_SENDER` | |
| `to` | `""` | `AUTO_TO` | `report --to` |
| `log_file` | `""` (no file) | `AUTO_LOG_FILE` | |

An empty environment value or a flag that was not given (`None`) does not count. A key in the file that is not in the table is **ignored with a warning** logged on stderr (set up logging before you read the settings, so the warning is shown).

**Logging** (p020): the `"auto"` logger; console on stderr at WARNING, INFO with `-v`, DEBUG with `-vv`; if `log_file` is set, a rotating file at DEBUG with timestamps.

**Every task run**:
1. holds the single-instance lock `<status_dir>/auto.lock` (p026; create `status_dir` if needed). If another live process holds it, print `auto: already running as process N` to stderr and return **3**, without doing any work, without writing a status file, and without touching the lock;
2. runs through the job runner (p027), which writes `<status_dir>/<task>.json` (`job`, `start`, `end`, `ok`, `result`, `error`; times from `now` when given) and returns **0** or **1**;
3. releases the lock afterwards, also when the task failed.

Usage errors are argparse's **2**.

**The tasks** (each returns a small dict that becomes the status file's `result`, and raises on failure):
- `tidy`: a missing folder raises. Otherwise plan and apply as in p006/p007, printing `would move: a.pdf -> documents/a.pdf` or `moved: ...` (forward slashes); result `{"moved": N, "dry_run": bool}`. With `--undo`: undo as in p007, print `restored N file(s)`, result `{"restored": N}`.
- `report`: read the CSV (UTF-8), `summarize` and `build_email` as in p021 with `sender` and `to` from the settings. No `to` raises. With `--dry-run`, print the subject and the body and send nothing. Otherwise, if `transport` is `None` raise (`"no mail transport configured"`: never pretend to have sent), else `transport.send_message(msg)`.
- `cleanup`: `delete_older_than(folder, keep_days, now, dry_run=not yes)` as in p013 (with all its safety checks), printing one line per file, `would delete: old.log` or `deleted: old.log` (relative to the folder, forward slashes).

## Example

```text
$ python solution.py --status-dir st tidy ~/Downloads --dry-run
would move: a.pdf -> documents/a.pdf
$ AUTO_KEEP_DAYS=14 python solution.py --status-dir st cleanup /tmp/cache
would delete: old.log
$ python solution.py --status-dir st report sales.csv --to boss@example.com; echo $?
ERROR auto.job: job report failed: no mail transport configured
1
$ cat st/report.json
{"job": "report", "start": "...", "ok": false, "result": null, "error": "RuntimeError: no mail transport configured", "end": "..."}
```

The tests run every task end to end in a temporary folder, check that dry runs change nothing, that a second instance exits with 3, that a failing task leaves a failed status and exit 1, that settings follow the precedence, and run the file once as a real program.
