# Plan, then move, with a dry run

Chapter section 3 (`plan_moves` and `apply_moves` in `tidylib.py`) and 1.3 (the four rules of safe automation: look before you leap, be able to undo). The trick that makes a dry run trustworthy is to split the work in two: **plan** (decide every move, change nothing) and **apply** (do exactly the plan). A dry run is then just "plan, and print instead of doing".

## What to write

The starter gives `CATEGORIES`, `JOURNAL = ".tidy-journal.json"`, `category_for` and `unique_destination` (problem p005). Write:

```python
def plan_moves(root) -> list[tuple[Path, Path]]: ...
def apply_moves(moves, root, dry_run=False) -> list[tuple[Path, Path]]: ...
```

`plan_moves(root)`:
- looks only at entries **directly** in `root`, sorted by name;
- skips folders (so the category folders made by an earlier run are left alone) and hidden files (name starts with `.`, which also skips the journal);
- pairs each file with `unique_destination(root / category_for(src) / src.name)`;
- changes **nothing** on disk.

`apply_moves(moves, root, dry_run=False)`:
- for each `(src, dst)`, unless `dry_run`: creates `dst.parent` if needed and moves the file with `shutil.move`;
- returns the list of pairs it did (or would do);
- if at least one file was really moved, writes the journal `root / JOURNAL`: JSON, a list of `[str(src), str(dst)]` pairs in the order they were moved (UTF-8);
- with `dry_run=True` touches **nothing**: no folders, no moves, no journal.

## Example

```python
# root holds: a.pdf, b.PNG, c (no suffix), .hidden, and an old folder images/
moves = plan_moves(root)
# [(root/'a.pdf', root/'documents/a.pdf'), (root/'b.PNG', root/'images/b.PNG'), (root/'c', root/'other/c')]
apply_moves(moves, root, dry_run=True)     # same list, nothing changed on disk
apply_moves(moves, root)                    # files moved, .tidy-journal.json written
plan_moves(root)                            # [] : a second run has nothing to do
```

The tests take a snapshot of the whole folder tree (every path and every file's bytes) before and after a dry run and require them to be equal.
