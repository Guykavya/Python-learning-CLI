import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_job(name, fn, status_dir):
    """Given (problem p027, shortened): run fn(), always write <status_dir>/<name>.json, return 0 or 1."""
    Path(status_dir).mkdir(parents=True, exist_ok=True)
    status = {"job": name, "start": datetime.now(timezone.utc).isoformat()}
    try:
        status.update(ok=True, result=fn(), error=None)
        code = 0
    except Exception as e:
        status.update(ok=False, result=None, error=f"{type(e).__name__}: {e}")
        code = 1
    status["end"] = datetime.now(timezone.utc).isoformat()
    (Path(status_dir) / f"{name}.json").write_text(json.dumps(status), encoding="utf-8")
    return code


TASKS = {}


def task(name):
    """Decorator: register fn in TASKS under name (ValueError if taken) and return fn unchanged."""
    def register(fn):
        if name in TASKS:
            raise ValueError(f"task {name!r} is already registered")
        TASKS[name] = fn
        return fn
    return register


@task("hello")
def hello(args):
    print("hello from a registered task")
    return "said hello"


@task("echo")
def echo(args):
    print(" ".join(args))
    return len(args)


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


if __name__ == "__main__":
    sys.exit(main())
