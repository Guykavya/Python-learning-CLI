## Hint 1

Start from the chapter's `tidy_click.py`. Which decorator turns a function into the group, and which one adds a command to it under a chosen name? What does `click.Path(exists=True, file_okay=False, path_type=Path)` save you from writing? Inside the commands, the only "logic" left should be calling the library and printing.

## Hint 2

```text
@click.group()
@click.version_option("1.0", prog_name="tidy")
def cli(): """Tidy a folder safely."""

@cli.command("organize")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("-n", "--dry-run", is_flag=True)
def organize_command(folder, dry_run):
    for src, dst in apply_moves(plan_moves(folder), folder, dry_run): click.echo(label + ...)

@cli.command("undo")
@click.argument("folder", ...same type...)
@click.confirmation_option(prompt="Put all moved files back?")
def undo_command(folder): click.echo(f"restored {len(undo(folder))} file(s)")
```
