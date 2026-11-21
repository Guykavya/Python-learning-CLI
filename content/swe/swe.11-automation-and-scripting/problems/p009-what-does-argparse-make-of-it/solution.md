## Approach

Checked by running the parser on Python 3.14 (the same result on 3.11):

| # | Line | Result | Why |
|---|---|---|---|
| 1 | `-vv organize x` | `command=organize dry_run=False folder=x verbose=2` | `-vv` is two counts, given **before** the subcommand where `-v` lives; `dry_run` gets its default |
| 2 | `organize --dry-run` | `exit 2` | `folder` is required: "the following arguments are required: folder" |
| 3 | `dupes x --min-size abc` | `exit 2` | `type=int` fails: "argument --min-size: invalid int value: 'abc'" |
| 4 | `dupes --min-size 0 x` | `command=dupes folder=x min_size=0 verbose=0` | options and positionals may come in any order inside a subcommand; `0` overrides the default `1` |
| 5 | `organize x -v` | `exit 2` | `-v` belongs to the main parser; after `organize` it is unknown: "unrecognized arguments: -v" |
| 6 | `organize -n "old photos"` | `command=organize dry_run=True folder=old photos verbose=0` | the shell removes the quotes, so `old photos` is **one** argument; the space survives |

Notice that the `Namespace` of `dupes` has no `dry_run` and the one of `organize` has no `min_size`: each subcommand adds only its own attributes.

Answers to the questions. Line 5 fails because global options belong to the main parser and must come before the subcommand; to accept `-v` in both places, add the same option to each sub-parser too (or to a shared `parents=[common]` parser), with `default=argparse.SUPPRESS` on the sub-parsers so they do not reset the count. In line 3 it is argparse's `type=int` that refuses: you get a clear message naming the option, exit code 2, and your own code never sees a string where it expects an int.

## Cost

Reading only. In practice: when a cron line misbehaves, run the same words through `build_parser().parse_args([...])` in a Python shell first.

## Another way

Run each line for real: `python tidy.py -vv organize x` with a `print(args)` in `main`. Do it **after** your prediction, to check yourself.
