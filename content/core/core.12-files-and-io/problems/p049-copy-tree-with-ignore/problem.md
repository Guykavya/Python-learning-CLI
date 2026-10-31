# Copy a project tree, skipping junk

Backups and deployments copy a folder but skip junk: `__pycache__`, `*.pyc`, `.git`, logs. `shutil.copytree` can do it
with its `ignore=` argument, and `shutil.ignore_patterns(...)` builds that argument from wildcard patterns.

Write `copy_project(src, dst, ignore=("__pycache__", "*.pyc", ".git"), overwrite=False)` in `solution.py`:

- Copy the folder `src` to `dst` with `shutil.copytree`.
- Skip every file **or folder**, at any depth, whose **name** matches one of the patterns in `ignore`.
- Also read the file `src/.copyignore` if it exists. Each line is one more pattern. Skip empty lines and lines that start
  with `#`. Remove spaces around a pattern. (The `.copyignore` file itself is copied like any other file.)
- If `dst` already exists and `overwrite` is `False`, `copytree` raises `FileExistsError`. Let it go up and change nothing.
  With `overwrite=True` merge into the existing folder (`dirs_exist_ok=True`).
- Return a sorted list of the files that are in `dst` afterwards, as relative paths with `/` (`Path.as_posix()`),
  folders are not listed.
- `src` must not be changed.

**Example**

```text
src/app.py
src/data/notes.log          (pattern *.log from .copyignore)
src/pkg/__pycache__/x.pyc
src/pkg/mod.py
src/.copyignore             lines:  # junk  /  *.log
```

`copy_project(src, dst)` returns `[".copyignore", "app.py", "pkg/mod.py"]`.
(`data/` is copied as an empty folder, but folders are not listed.)
