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
        # TODO
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
    # TODO: prog="auto", --status-dir, subcommands list and run NAME ARGS...
    return argparse.ArgumentParser(prog="auto")


def main(argv=None):
    # TODO
    return 0


if __name__ == "__main__":
    sys.exit(main())
