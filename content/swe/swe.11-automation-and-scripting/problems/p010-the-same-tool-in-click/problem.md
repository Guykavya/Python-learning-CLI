# The same tool in Click

Chapter section 5.1 (Click) and 5.4 (which to choose? keep the CLI thin). Click builds a command line from decorators, validates paths for you, asks "are you sure?" and ships a test runner, `click.testing.CliRunner`, so no subprocess is needed in tests.

## What to write

The starter holds the tidy library (`plan_moves`, `apply_moves`, `undo`, ...), exactly as in the argparse version. Below it, write a Click group `cli` with two commands that call **those same functions** (do not copy their logic into the commands):

```text
cli                      group; --version prints "tidy, version 1.0" (click.version_option("1.0", prog_name="tidy"))
  organize FOLDER [-n/--dry-run]
  undo FOLDER [--yes]
```

- `FOLDER` uses `click.Path(exists=True, file_okay=False, path_type=Path)`: a missing folder or a file is a usage error (Click exits with code 2 and says why).
- `organize` prints one line per move with `click.echo`: `moved: a.pdf -> documents/a.pdf`, or `would move: ...` with `--dry-run`. Use `dst.relative_to(folder).as_posix()` so the output looks the same on Windows.
- `undo` asks `Put all moved files back?` with `click.confirmation_option` before doing anything; `--yes` skips the question. Answering no aborts with exit code 1 and changes nothing. After undoing it prints `restored N file(s)`.
- The Python function names of the commands are `organize_command` and `undo_command` (so they do not hide the library's `undo`); register them under the names `organize` and `undo` with `@cli.command("organize")`.
- End the file with `if __name__ == "__main__": cli()`.

## Example

```python
from click.testing import CliRunner
runner = CliRunner()
r = runner.invoke(cli, ["organize", "mess", "--dry-run"])
r.exit_code, r.output.splitlines()[0]      # (0, 'would move: README -> other/README')
r = runner.invoke(cli, ["undo", "mess"], input="n\n")
r.exit_code                                # 1  ('Aborted!', nothing changed)
r = runner.invoke(cli, ["organize", "no-such-folder"])
r.exit_code                                # 2  (Error: ... 'no-such-folder' does not exist.)
```
