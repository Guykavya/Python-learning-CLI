## Hint 1

Start with the tree: `a.py`, `ab.py`, `notes.txt`, `.hidden.py` and a folder `sub` with `c.py` and `d.txt`.
Which of them does `root.glob("*.py")` see? Does `*` skip a name that starts with a dot in `pathlib`?

## Hint 2

Go line by line.

```
glob("*.py")      -> only the top folder
glob("*/*.py")    -> exactly one folder level down
glob("**/*.py")   -> the top folder AND every level below
rglob("*.txt")    -> the same as glob("**/*.txt")
glob("*")         -> every entry in the top folder, files and folders
fnmatch           -> compares names as plain text; "*" also matches "/"
Path.match        -> compares from the right-hand side
```
