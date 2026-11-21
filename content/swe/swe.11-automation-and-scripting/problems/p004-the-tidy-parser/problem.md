# The tidy parser

Chapter section 3 (the `tidy.py` command line) and 3.1 (argparse in one table). `tidy` is one tool with several jobs, so it uses **subcommands**: `tidy organize`, `tidy undo`, `tidy dupes`. This problem is only the parser: no files are touched.

## What to write

`build_parser()` returning an `argparse.ArgumentParser` with `prog="tidy"` and:

| Where | Argument | Details |
|---|---|---|
| global (before the subcommand) | `-v`, `--verbose` | counted: `-v` is 1, `-vv` is 2, default `0`; the attribute is `verbose` |
| global | `--version` | prints `tidy 1.0` and exits 0 |
| subcommands | `dest="command"`, `required=True` | no subcommand is a usage error |
| `organize` | `folder` (`type=Path`), `-n` / `--dry-run` | the flag is `dry_run`, default `False` |
| `undo` | `folder` (`type=Path`) | nothing else |
| `dupes` | `folder` (`type=Path`), `--min-size` | `type=int`, `default=1`, `metavar="BYTES"`; the attribute is `min_size` |

Give every subcommand a one-line `help=` so `tidy --help` lists them.

## Example

```python
p = build_parser()
p.parse_args(["-vv", "organize", "Downloads"])
# Namespace(verbose=2, command='organize', folder=PosixPath('Downloads'), dry_run=False)
p.parse_args(["dupes", "x", "--min-size", "10"]).min_size     # 10 (an int, not "10")
p.parse_args([])                                               # usage error: SystemExit(2)
p.parse_args(["--help"])                                       # prints help, SystemExit(0)
```

The tests call `build_parser().parse_args(...)` directly and also run your file once as a real program (`python solution.py --help`), so keep the `__main__` block of the starter.
