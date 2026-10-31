## Hint 1

For `"mathkit/stats/mean.py"`, which folders need an `__init__.py`? `PurePosixPath("mathkit/stats/mean.py").parents`
gives `mathkit/stats`, `mathkit` and `.`. Which one do you skip?

## Hint 2

```
all_files = dict(files)                   # copy, do not change the caller's dict
for rel in files:
    for folder in PurePosixPath(rel).parents:
        if str(folder) == ".": continue
        all_files.setdefault(f"{folder}/__init__.py", "")
for rel, text in all_files.items():
    target = Path(root) / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
return sorted(all_files)
```
