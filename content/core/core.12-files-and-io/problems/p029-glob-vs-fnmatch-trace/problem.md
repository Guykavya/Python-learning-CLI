# Trace: glob, rglob and fnmatch

`Path.glob` looks at files **on disk**. `fnmatch` only compares **strings**. Their rules for `*` and `**`
are not the same. The program builds a small folder in a temporary place, so the output has no paths in it.

```python
import fnmatch
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "sub").mkdir()
    for name in ["a.py", "ab.py", "notes.txt", ".hidden.py", "sub/c.py", "sub/d.txt"]:
        (root / name).write_text("x")

    print(sorted(p.name for p in root.glob("*.py")))
    print(sorted(p.name for p in root.glob("*/*.py")))
    print(sorted(p.name for p in root.glob("**/*.py")))
    print(sorted(p.name for p in root.rglob("*.txt")))
    print(len(list(root.glob("*"))))

    names = [p.name for p in root.iterdir()]
    print(sorted(fnmatch.filter(names, "?.py")))
    print(sorted(fnmatch.filter(names, "[ab]*")))
    print(fnmatch.fnmatchcase("sub/c.py", "*.py"))
    print(fnmatch.fnmatchcase("A.PY", "*.py"))
    print(Path("sub/c.py").match("*.py"), Path("sub/c.py").match("sub/*.py"), Path("sub/c.py").match("c.py"))
```

Write exactly what the program prints to **standard output**, one line for each printed line, in `answer.txt`.
The program never ends with a traceback. Lines sent to `sys.stderr` do not count.

Hints: `sorted` makes the order fixed. Think about what `*` does with a leading dot, with a slash, and
what `?` and `[ab]` match.
