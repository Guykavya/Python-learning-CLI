## Approach

```python
@click.group()
@click.version_option("1.0", prog_name="tidy")
def cli():
    """Tidy a folder safely."""


@cli.command("organize")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("-n", "--dry-run", is_flag=True, help="Show what would happen, change nothing.")
def organize_command(folder, dry_run):
    """Move files into folders by type."""
    label = "would move" if dry_run else "moved"
    for src, dst in apply_moves(plan_moves(folder), folder, dry_run):
        click.echo(f"{label}: {src.name} -> {dst.relative_to(folder).as_posix()}")


@cli.command("undo")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.confirmation_option(prompt="Put all moved files back?")
def undo_command(folder):
    """Reverse the last organize."""
    click.echo(f"restored {len(undo(folder))} file(s)")
```

The commands are a few lines each because the library does the work. That is the payoff of a thin CLI layer: the argparse tool of p007 and this Click tool are two front ends to **one** core, and a bug fixed in `plan_moves` is fixed in both. Click adds safety for free: path validation (exit 2 with a clear message) and a confirmation for the risky command.

## Complexity

The same as the library: O(n log n) to plan, one move per file.

## Another way

Typer (chapter 5.2) writes the same commands with type hints (`folder: Annotated[Path, typer.Argument(exists=True, file_okay=False)]`) and is built on Click, so `typer.testing.CliRunner` works the same way. Try it on your machine; it is not installed in the course environment.
