## Approach

```python
def undo(root):
    journal = Path(root) / JOURNAL
    if not journal.exists():
        return []
    restored = []
    for s, d in reversed(json.loads(journal.read_text(encoding="utf-8"))):
        s, d = Path(s), Path(d)
        if d.exists() and not s.exists():
            shutil.move(str(d), str(s))
            restored.append((d, s))
            try:
                d.parent.rmdir()          # only succeeds if the folder is now empty
            except OSError:
                pass
    journal.unlink()
    return restored


def main(argv=None):
    args = build_parser().parse_args(argv)
    folder = args.folder
    if not folder.is_dir():
        print(f"tidy: error: {folder} is not a folder", file=sys.stderr)
        return 1
    if args.command == "organize":
        moves = apply_moves(plan_moves(folder), folder, args.dry_run)
        label = "would move" if args.dry_run else "moved"
        for src, dst in moves:
            print(f"{label}: {src.name} -> {dst.relative_to(folder).as_posix()}")
        summary = "to move" if args.dry_run else "moved"
        print(f"{len(moves)} file(s) {summary}", file=sys.stderr)
    else:
        print(f"restored {len(undo(folder))} file(s)")
    return 0
```

The three guarantees come from three small decisions: **plan first** (dry run is honest), **skip folders and hidden files** (run two finds nothing), and **a journal checked before each step back** (undo is exact and never overwrites). Each one has its own test, so a later change that breaks a guarantee fails loudly.

## Complexity

O(n) moves for n journal entries, plus O(n log n) for planning.

## Another way

Keep several journals (`.tidy-journal-2026-11-21T0930.json`) so you can undo older runs, not only the last one. `undo` then takes the newest by name. Or move to a dated trash folder instead of a journal when the operation is a delete (section 6.4).
