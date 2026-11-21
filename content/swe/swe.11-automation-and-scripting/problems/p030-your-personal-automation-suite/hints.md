## Hint 1

Write it in layers and test each layer before the next, exactly like the chapter's suite layout (section 15): the **tasks** are plain functions that take values and return a dict (no argparse, no logging setup, no `sys.exit`); `load_settings` and `setup_logging` are separate helpers; `main` only parses, loads settings, sets up logging, takes the lock, and hands one zero-argument function to `run_job`. Which value must `main` give `run_job` so that the task's arguments are already bound? (A `lambda` or a small nested `def`.)

## Hint 2

```text
main(argv, env, transport, now):
    args = build_parser().parse_args(argv)                  # usage errors: SystemExit(2)
    setup_logging(args.verbose)                             # so warnings while loading settings are shown
    flags = {"status_dir": args.status_dir, "keep_days": getattr(args, "days", None), "to": getattr(args, "to", None)}
    settings = load_settings(args.config, env, flags)
    setup_logging(args.verbose, settings["log_file"] or None)
    clock = (lambda: now) if now is not None else (lambda: datetime.now(timezone.utc))
    status_dir = Path(settings["status_dir"]); status_dir.mkdir(parents=True, exist_ok=True)
    job = the task function with its arguments bound (tidy / report / cleanup)
    try:
        with single_instance(status_dir / "auto.lock"):
            return run_job(args.command, job, status_dir, clock)
    except AlreadyRunning as e: print(f"auto: {e}", file=sys.stderr); return 3
```
