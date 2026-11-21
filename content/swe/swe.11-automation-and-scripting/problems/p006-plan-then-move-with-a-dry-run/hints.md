## Hint 1

`plan_moves` only *looks*: `iterdir()`, `is_file()`, a name check, and the two helpers. Not a single call that writes. In `apply_moves`, where exactly does the `if not dry_run` belong so that the returned list is the same in both modes, but nothing is created in a dry run, not even the category folder or the journal?

## Hint 2

```text
plan_moves:
    moves = []
    for src in sorted(Path(root).iterdir()):
        if src is a file and its name does not start with ".":
            moves.append((src, unique_destination(Path(root) / category_for(src) / src.name)))
apply_moves:
    done = []
    for src, dst in moves:
        if not dry_run: dst.parent.mkdir(exist_ok=True); shutil.move(str(src), str(dst))
        done.append((src, dst))
    if done and not dry_run: write json.dumps([[str(s), str(d)] for s, d in done]) to root / JOURNAL
    return done
```
