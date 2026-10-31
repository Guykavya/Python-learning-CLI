## Approach

Separate **planning** from **doing**. `plan_moves` only reads the disk and returns a list of `(source, target)` pairs.
It keeps a set of reserved target names so two files never plan the same name. `main` then prints and, when it is not a
dry run, moves. Because both modes use the same plan, the dry run is exact. Check the arguments before you change
anything, so an error leaves the disk as it was. Idempotence comes for free: after the first run no files are left in
the top level, so the plan is empty.

## Code

```python
import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

TYPES = {
    ".jpg": "images", ".jpeg": "images", ".png": "images", ".gif": "images",
    ".pdf": "documents", ".doc": "documents", ".docx": "documents", ".txt": "documents", ".md": "documents",
    ".csv": "data", ".json": "data", ".xml": "data", ".toml": "data",
    ".py": "code", ".js": "code", ".html": "code", ".css": "code",
    ".zip": "archives", ".tar": "archives", ".gz": "archives",
}


def folder_for(path, by):
    if by == "type":
        return TYPES.get(path.suffix.lower(), "other")
    info = path.stat()
    if by == "date":
        return datetime.fromtimestamp(info.st_mtime).strftime("%Y-%m")
    if info.st_size < 1024:
        return "small"
    if info.st_size < 102400:
        return "medium"
    return "large"


def unique_target(folder, name, reserved):
    target = folder / name
    base = Path(name)
    number = 0
    while target.exists() or target in reserved:
        number += 1
        target = folder / f"{base.stem}_{number}{base.suffix}"
    return target


def build_parser():
    parser = argparse.ArgumentParser(prog="organiser", description="Sort the files of a folder into sub-folders.")
    parser.add_argument("source", help="folder with the messy files")
    parser.add_argument("--by", choices=["type", "date", "size"], default="type")
    parser.add_argument("--dest", help="folder to put the sub-folders in (default: the source folder)")
    parser.add_argument("--dry-run", action="store_true", help="show what would happen, change nothing")
    return parser


def plan_moves(source, dest, by):
    files = [p for p in source.iterdir() if p.is_file() and not p.name.startswith(".")]
    files.sort(key=lambda p: p.name)
    reserved = set()
    plan = []
    for path in files:
        target = unique_target(dest / folder_for(path, by), path.name, reserved)
        reserved.add(target)
        plan.append((path, target))
    return plan


def main(argv=None):
    args = build_parser().parse_args(argv)
    source = Path(args.source)
    if not source.is_dir():
        print(f"error: {source} is not a folder", file=sys.stderr)
        return 2
    dest = Path(args.dest) if args.dest else source
    if dest.exists() and not dest.is_dir():
        print(f"error: {dest} is not a folder", file=sys.stderr)
        return 2

    plan = plan_moves(source, dest, args.by)
    if not plan:
        print("nothing to do")
        return 0

    verb = "would move" if args.dry_run else "moved"
    done = 0
    failed = 0
    for path, target in plan:
        if not args.dry_run:
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path), str(target))
            except OSError as error:
                print(f"error: cannot move {path.name}: {error}", file=sys.stderr)
                failed += 1
                continue
        print(f"{verb} {path.name} -> {target.relative_to(dest).as_posix()}")
        done += 1
    print(f"{verb} {done} file{'' if done == 1 else 's'}")
    return 1 if failed else 0
```

## Complexity

Time O(F log F) for F files (the sort) plus the cost of the moves. Memory O(F) for the plan.

## Another way

- Put the categories in a dict from extension to folder name (as above), or in a TOML file that the user can edit.
- Use `parser.set_defaults(func=...)` if you later add more commands.
- For `date`, you could use the creation time, but `st_ctime` means different things on Linux and Windows, so
  the modification time is the more portable choice.
- Add `--undo`: write a JSON log of the moves and move the files back.
