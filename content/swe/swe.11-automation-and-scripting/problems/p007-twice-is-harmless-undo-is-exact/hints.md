## Hint 1

Why must undo walk the journal **backwards**? Think of a file that was renamed `a (1).pdf` because `a.pdf` was taken. And when may undo *not* move a file back? Ask: what if the user created a new `a.pdf` in the meantime? After a file goes back, how can you remove its folder only when it is empty, without listing it? (`rmdir` refuses non-empty folders with an `OSError`.)

## Hint 2

```text
undo(root):
    journal = root / JOURNAL; if missing: return []
    for s, d in reversed(json.loads(journal text)):
        if Path(d).exists() and not Path(s).exists():
            shutil.move(d, s); restored.append((d, s))
            try: Path(d).parent.rmdir()  except OSError: pass
    journal.unlink(); return restored
main:
    args = build_parser().parse_args(argv)
    if not args.folder.is_dir(): error to stderr; return 1
    organize: moves = apply_moves(plan_moves(folder), folder, args.dry_run); print lines; print count to stderr
    undo: print(f"restored {len(undo(folder))} file(s)")
    return 0
```
