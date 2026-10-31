# A context manager that restores the folder

`os.chdir(path)` changes the **current working directory** of the whole program. If you forget to change it back,
every later relative path points somewhere else. This is exactly the job for a context manager.

Write `working_dir(path)` in `solution.py` with `@contextlib.contextmanager`:

- On entering, remember the current folder (`os.getcwd()`) and change to `path`.
- It **yields** the new folder as a `Path` (`Path.cwd()`).
- On leaving, **always** go back to the old folder, also when the `with` body raised an error.
  Do not hide the error.
- If `path` does not exist, `os.chdir` raises `FileNotFoundError`. Let it go up, and the current folder stays the same.

**Example**

```python
with working_dir("/some/folder") as here:
    Path("note.txt").write_text("hi")   # created inside /some/folder
# back in the old folder here
```
