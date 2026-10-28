## Hint 1

What does `shutil.ignore_patterns(*patterns)` return, and where do you pass it? How do you collect the extra patterns
from `.copyignore`: which lines are real patterns? How can you list only the files of `dst` afterwards?

## Hint 2

```
patterns = list(ignore)
file = Path(src) / ".copyignore"
if file.exists():
    for line in file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"): patterns.append(line)
shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*patterns), dirs_exist_ok=overwrite)
return sorted(p.relative_to(dst).as_posix() for p in Path(dst).rglob("*") if p.is_file())
```
