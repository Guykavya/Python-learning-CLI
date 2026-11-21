## Approach

```python
def task(name):
    def register(fn):
        if name in TASKS:
            raise ValueError(f"task {name!r} is already registered")
        TASKS[name] = fn
        return fn
    return register


def build_parser():
    p = argparse.ArgumentParser(prog="auto", description="My automation suite.")
    p.add_argument("--status-dir", default="status", help="where status files are written")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="show the tasks")
    run = sub.add_parser("run", help="run one task")
    run.add_argument("name")
    run.add_argument("args", nargs=argparse.REMAINDER, help="passed to the task")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "list":
        for name in sorted(TASKS):
            print(name)
        return 0
    if args.name not in TASKS:
        print(f"auto: unknown task {args.name!r}; known tasks: {', '.join(sorted(TASKS))}", file=sys.stderr)
        return 2
    fn = TASKS[args.name]
    return run_job(args.name, lambda: fn(args.args), args.status_dir)
```

The registry makes the suite **open for additions**: a new task is one function with `@task("name")`, and it automatically appears in `list`, can be run, and is wrapped by the runner, so it writes a status file and returns an honest exit code without any code of its own for that. The CLI stays thin (section 15's rule): tasks do not parse arguments or configure logging.

## Complexity

O(1) to look up a task; O(t log t) to list t tasks.

## Another way

Give each task its own argparse sub-parser (the task registers a function *and* a small `add_arguments(parser)` hook), so `auto run check-disk --min-free 5` is validated with real types and `--help`. Bigger suites use entry points (`[project.entry-points."auto.tasks"]` in `pyproject.toml`, section 14) so tasks can live in separate packages and still be discovered.
