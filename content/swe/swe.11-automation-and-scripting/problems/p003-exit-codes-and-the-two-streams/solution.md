## Approach

```python
def list_files(folder, ext=None):
    names = []
    for p in sorted(Path(folder).iterdir()):
        if p.is_file() and not p.name.startswith("."):
            if ext is None or p.suffix.lower() == ext.lower():
                names.append(p.name)
    return names


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.folder.is_dir():
        print(f"listfiles: error: {args.folder} is not a folder", file=sys.stderr)
        return 1
    names = list_files(args.folder, args.ext)
    for name in names:
        print(name)
    print(f"{len(names)} file(s)", file=sys.stderr)
    return 0
```

Three channels, three jobs: stdout carries data that pipes can trust, stderr carries the human story, the exit code carries the verdict that `&&`, cron and CI read. The message format `prog: error: ...` copies argparse's own, so a user sees the same style for every error.

## Complexity

O(n log n) for n entries in the folder (sorting).

## Another way

Use `logging` for the summary and the error (`log.info`, `log.error`) with a handler on stderr, as the skeleton of section 2.2 does. For a tiny tool `print(..., file=sys.stderr)` is enough; once there are levels (`-v`) and a log file, switch to logging.
