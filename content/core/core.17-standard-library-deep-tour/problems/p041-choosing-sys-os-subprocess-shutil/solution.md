See the model answer shown when you check. The ideas that must appear:

1. `sys.executable` inside an argument list for `subprocess.run`: the same interpreter and venv; `"python"` may be a different one.
2. `os.environ.get(name, default)`: no `KeyError` when missing.
3. `shutil.copytree`: a whole tree; `shutil.copy` / `os` handle one file or need a hand-written walk.
4. `shutil.rmtree`: `os.rmdir` only removes empty folders. Dangerous, check the path first.
5. `shutil.which("git")`: searches `PATH` (and `.exe` on Windows) without running anything.
6. `subprocess.run([...], capture_output=True, text=True, check=True).stdout`: a list, no shell, captured text, errors raise.
7. `print(..., file=sys.stderr)` + `sys.exit(2)`: errors on stderr; `SystemExit` still runs cleanup.
8. `os.system` with a built string: not portable (`cp` is not on Windows), breaks on spaces and allows shell injection, returns only a status (no exception, no captured output).
