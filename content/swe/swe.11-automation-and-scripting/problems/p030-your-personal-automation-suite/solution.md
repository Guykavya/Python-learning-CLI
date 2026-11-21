## Approach

The reference (`reference.py`) is the earlier problems glued together by a thin `main`:

```python
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
        job = lambda: tidy_task(args.folder, args.dry_run, args.undo)
    elif args.command == "report":
        job = lambda: report_task(args.csv_file, settings["sender"], settings["to"], transport, args.dry_run)
    else:
        job = lambda: cleanup_task(args.folder, settings["keep_days"], clock(), args.yes)

    try:
        with single_instance(status_dir / "auto.lock"):
            return run_job(args.command, job, status_dir, clock)
    except AlreadyRunning as e:
        print(f"auto: {e}", file=sys.stderr)
        return 3
```

How each requirement of section 16 is met:

| Requirement | Where |
|---|---|
| look before you leap | `tidy --dry-run`, `report --dry-run`, and `cleanup` is a dry run unless `--yes` |
| be able to undo | `tidy --undo` and the journal; cleanup refuses `/` and the home folder and never follows symlinks |
| safe to run twice | tidy skips folders and hidden files; the lock stops two runs at once (exit 3) |
| fail loudly | every task raises on failure; `run_job` turns it into exit 1, a log line and a `failed` status |
| configurable, no secrets in code | `load_settings`: defaults < file < `AUTO_*` < flags; unknown keys are warned about |
| unattended | status files with start and end times, ready for `problem_with` (p027) to catch silence |

The order inside `main` matters in two places: logging is set up **before** the settings are read (so a typo in the config file is reported), and `AlreadyRunning` is raised **before** `run_job`, so a refused run leaves no status file that would hide the real run's result.

## Complexity

Each task as in its own problem: O(n log n) for n files in tidy and cleanup, O(rows) for the report.

## Another way

Split the single file into the package of section 15 (`auto/cli.py`, `auto/settings.py`, `auto/tasks/tidy.py`, ...) and add a task registry (p029), so a fourth task is one decorated function. Then install it with `pip install -e .` and a `[project.scripts] auto = "auto.cli:main"` entry (section 14), and schedule it with the `cron_line` of p025: `0 8 * * 1 cd /home/me/automation && /home/me/venv/bin/python -m auto report /home/me/exports/sales.csv >> /home/me/automation/auto.log 2>&1`. Your README answers the four questions of section 16.5.
