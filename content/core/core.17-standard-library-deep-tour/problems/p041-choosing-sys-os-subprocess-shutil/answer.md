**1. Same Python.** `subprocess.run([sys.executable, "helper.py", ...])`. `sys.executable` is the full path
of the running interpreter, so the helper sees the same virtual environment and packages. Typing `"python"`
may start a different Python (or none at all on Windows, where it is often `py`).

**2. Environment variable.** `os.environ.get("BACKUP_DIR", "backups")`. `os.environ` is a dict-like view
of the environment; `os.environ["BACKUP_DIR"]` would raise `KeyError` when it is missing.

**3. Copy a tree.** `shutil.copytree(src, dst)`. It walks the folders, creates them and copies every file
(with `copy2`, keeping times). With `os` alone you would write the walk and the byte copying yourself;
`shutil.copy` copies just one file.

**4. Delete a non-empty folder.** `shutil.rmtree(path)`. `os.rmdir` only removes an **empty** folder
and `os.remove` only removes files. It is dangerous: it deletes without asking, so check the path first.

**5. Is git installed?** `shutil.which("git")` returns the full path or `None`. It searches `PATH` the
same way the shell does, including `.exe` on Windows, without starting anything.

**6. Run git and capture.** `subprocess.run(["git", "status", "--short"], capture_output=True, text=True,
check=True).stdout`. A **list** of arguments, no shell; `capture_output` gives the text back instead
of printing it; `check=True` raises `CalledProcessError` if git fails, so the error is not silently ignored.
`os.system` cannot capture output at all.

**7. Exit with code 2.** `print("error: ...", file=sys.stderr)` then `sys.exit(2)`. Errors go to
**stderr** so they do not mix with real output when stdout is redirected; `sys.exit(2)` raises
`SystemExit`, so `finally` blocks and `with` blocks still clean up (`os._exit` would skip them).

**8. Why not `os.system("cp -r " + src + " " + dst)`?**
- **Not portable**: `cp` does not exist in the Windows command prompt; `shutil.copytree` works everywhere.
- **Breaks and is unsafe with special characters**: a path with a space becomes two arguments, and a
  name like `x; rm -rf ~` makes the shell run a second command (shell injection).
- **No real error handling or output**: you only get an exit status number back, no exception, no
  captured message; you must remember to check it.
- (Also: it starts a whole shell process just to copy files that Python can copy itself.)

**Rule of thumb.** Do it in Python (`os`, `shutil`, `pathlib`) when Python can; use `subprocess`
only to run a real external program, always with an argument list; use `sys` for the interpreter's own
facts (`argv`, `executable`, `stdin/stdout/stderr`, `exit`, `platform`).
