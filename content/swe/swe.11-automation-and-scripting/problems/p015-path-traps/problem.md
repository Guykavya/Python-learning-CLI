# Path traps

Chapter sections 6.1 (pathlib in ten lines), 6.2 (traps with paths and files) and 6.4 (`is_inside` resolves first). `pathlib` is the right tool, but a few of its answers surprise almost everyone the first time. Predict what this program prints.

`PurePosixPath` is a path that only does the string rules of Linux and macOS and never touches the disk, so lines 1, 2, 3 and 5 print the same on every computer. Lines 4 and 6 use a real temporary folder, and print only names and booleans, so they are the same everywhere too.

```python
import tempfile
from pathlib import Path, PurePosixPath

print(1, PurePosixPath("data") / "/etc/passwd")
print(2, PurePosixPath("backup.tar.gz").suffix)
print(3, PurePosixPath("backup.tar.gz").stem)

folder = Path(tempfile.mkdtemp())
(folder / ".env").write_text("SECRET=1", encoding="utf-8")
(folder / "a.txt").write_text("a", encoding="utf-8")
(folder / "sub").mkdir()
(folder / "sub" / "b.txt").write_text("b", encoding="utf-8")
print(4, sorted(p.name for p in folder.glob("*")))

print(5, PurePosixPath("notes.backup.txt").with_suffix(""))

base = folder / "sandbox"
base.mkdir()
escape = base / ".." / "secret.txt"
print(6, escape == folder / "secret.txt", escape.resolve() == folder.resolve() / "secret.txt")
```

## Answer format

Write the six lines exactly as `print` shows them (the number, a space, then the value) in `answer.txt`. A list prints like `['x', 'y']`.

## After you answer

- Line 1 is how a cleanup script ends up working in `/etc` when a config value starts with `/`. What check from section 6.4 would catch it before anything happens?
- Line 4: `glob.glob("*")` from the `glob` module behaves differently from `Path.glob("*")` here. Which one would your cleanup script use, and what does that mean for a file called `.env`?
