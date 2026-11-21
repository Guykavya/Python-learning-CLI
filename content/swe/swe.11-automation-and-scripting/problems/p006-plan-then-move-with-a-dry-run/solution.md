## Approach

```python
def plan_moves(root):
    moves = []
    for src in sorted(Path(root).iterdir()):
        if src.is_file() and not src.name.startswith("."):
            moves.append((src, unique_destination(Path(root) / category_for(src) / src.name)))
    return moves


def apply_moves(moves, root, dry_run=False):
    done = []
    for src, dst in moves:
        if not dry_run:
            dst.parent.mkdir(exist_ok=True)
            shutil.move(str(src), str(dst))
        done.append((src, dst))
    if done and not dry_run:
        (Path(root) / JOURNAL).write_text(json.dumps([[str(s), str(d)] for s, d in done]), encoding="utf-8")
    return done
```

Because the plan is a plain list, the dry run prints *exactly* what the real run will do, and the journal is simply the same list written to disk, which is all `undo` needs (p007). Skipping folders and hidden files makes the second run harmless: after the first run every file is inside a category folder, and the journal itself starts with a dot.

## Complexity

O(n log n) for sorting n entries, plus one move per file.

## Another way

Write the journal **before** moving, then append to it as you go (or rewrite it after each move). If the script crashes halfway, the journal still lists the moves that happened, so undo can repair a half-finished run. The chapter's version writes it at the end, which is simpler but loses that information on a crash.
