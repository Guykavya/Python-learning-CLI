## Hint 1

Which lines are data that another program might want to read (`| wc -l`, `| sort`)? Only those go to `print(...)`. Everything for the human gets `file=sys.stderr`. And where does the verdict go? Not into a printed word, but into the number `main` returns.

## Hint 2

```text
list_files: [p.name for p in sorted(Path(folder).iterdir())
             if p.is_file() and not p.name.startswith(".") and (ext is None or p.suffix.lower() == ext.lower())]
main:
    args = build_parser().parse_args(argv)        # usage errors exit 2 by themselves
    if not args.folder.is_dir(): print error to stderr; return 1
    for name in list_files(...): print(name)
    print(f"{len(names)} file(s)", file=sys.stderr); return 0
```
