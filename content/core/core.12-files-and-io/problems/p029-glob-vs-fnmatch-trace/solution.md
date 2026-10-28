## Approach

The tree has five entries at the top level: `a.py`, `ab.py`, `notes.txt`, `.hidden.py` and the folder `sub`.

1. `glob("*.py")` looks only at the top level. In `pathlib` a leading dot is **not** special, so `.hidden.py` is
   included. Sorting puts `.` first.
2. `glob("*/*.py")` means "one folder, then a file". Only `sub/c.py` fits.
3. `glob("**/*.py")` means "this folder and all folders below". It finds the top-level files and `c.py`.
4. `rglob("*.txt")` is the short form of `glob("**/*.txt")`: `d.txt` and `notes.txt`.
5. `glob("*")` returns 5 entries. Folders count too.
6. `fnmatch.filter` works on the **names** in the list. `?.py` is one character and `.py`, so only `a.py`.
   `[ab]*` is "starts with a or b".
7. `fnmatchcase("sub/c.py", "*.py")` is `True`: in `fnmatch` the `*` also matches a slash.
8. `fnmatchcase("A.PY", "*.py")` is `False` because case matters.
9. `Path.match` compares from the right, so `c.py`, `*.py` and `sub/*.py` all match `sub/c.py`.

## Output

```text
['.hidden.py', 'a.py', 'ab.py']
['c.py']
['.hidden.py', 'a.py', 'ab.py', 'c.py']
['d.txt', 'notes.txt']
5
['a.py']
['a.py', 'ab.py']
True
False
True True True
```

## Complexity

Not applicable.

## Another way

Run the program again and print the full list instead of only `.name`. You will see that `glob` gives back
`Path` objects for files **and** folders, in an order that depends on the disk.
