# Keep the command line thin

Chapter sections 2.2 (the skeleton: why each piece exists), 3 (`tidylib.py` has no command-line code at all), 5.4 (which to choose? keep the logic in plain functions) and "Try it: spot the thin layer". A teammate wrote their tool like this:

```python
@click.command()
@click.argument("folder")
@click.option("--dry-run", is_flag=True)
def organize(folder, dry_run):
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if os.path.isfile(path) and not name.startswith("."):
            ext = os.path.splitext(name)[1].lower()
            target = os.path.join(folder, CATEGORIES.get(ext, "other"))
            if dry_run:
                click.echo(f"would move {name}")
            else:
                os.makedirs(target, exist_ok=True)
                shutil.move(path, os.path.join(target, name))
                click.echo(f"moved {name}")
```

It works. In `answer.md` (about 250 to 400 words), explain why the course keeps the logic in plain functions (`plan_moves`, `apply_moves`, `undo`) and lets the command-line layer only **parse, call and print**:

1. **Testing.** What does a test of this command need, compared with a test of `plan_moves(root)`? Which behaviours are hard to test here (think about the dry run, and about the overwrite rule this code silently breaks)?
2. **Two front ends, one core.** The course has an argparse `tidy.py` (p007) and a Click `tidy_click.py` (p010). What happens to a bug fix in this design if you have both? What would moving to Typer cost in each design?
3. **Reuse.** A scheduled job (section 13's `run_job`) and the task suite (section 15) need to call "organize" with no terminal and no command-line arguments. How would they call this code?
4. **Where does a change go?** Answer the chapter's "spot the thin layer" for the thin design: a bug where `.JPG` lands in `other`, and renaming `--dry-run` to `--preview`.
5. **A checklist** of 4 to 6 rules for a thin CLI layer that you would apply in a code review.

## Example

A good sentence for part 1: "To test this command I need `CliRunner`, a temporary folder and string matching on the output; to test `plan_moves` I call a function and compare a list. And the dry run is only *trusted* because both paths happen to use the same `if`; with plan-then-apply the dry run prints the very list the real run executes."
