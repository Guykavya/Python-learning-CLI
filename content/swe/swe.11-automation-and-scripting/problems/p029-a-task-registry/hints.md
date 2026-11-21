## Hint 1

A decorator with an argument is a function that **returns** a decorator: `task("hello")` runs first and gives back `register`, and Python then calls `register(hello)`. What must `register` return so that `hello` is still the same function afterwards? Why must `main` look the task up in `TASKS` **itself** rather than using `choices=` in argparse (look at the exit code and message the task wants)?

## Hint 2

```text
def task(name):
    def register(fn):
        if name in TASKS: raise ValueError(f"task {name!r} is already registered")
        TASKS[name] = fn; return fn
    return register
build_parser: p = ArgumentParser(prog="auto"); p.add_argument("--status-dir", default="status")
    sub = p.add_subparsers(dest="command", required=True); sub.add_parser("list")
    r = sub.add_parser("run"); r.add_argument("name"); r.add_argument("args", nargs=argparse.REMAINDER)
main: args = parse; if list: print sorted names; return 0
    if args.name not in TASKS: print error with ", ".join(sorted(TASKS)) to stderr; return 2
    return run_job(args.name, lambda: TASKS[args.name](args.args), args.status_dir)
```
