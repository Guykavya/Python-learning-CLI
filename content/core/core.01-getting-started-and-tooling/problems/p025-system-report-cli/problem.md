# Project: personal system report

Build the module project: a command-line script that prints a report about the
computer and the Python running it.

The script reads one line, a **nickname**, with `input()` (no prompt), and
prints exactly:

```
==============================
System report for <nickname>
==============================
User: <value of the USER environment variable, or unknown>
Python: <version> (<implementation>)
OS: <system> <release>
Machine: <machine>
Folder: <current working directory>
In venv: <True or False>
==============================
```

| Value | Source |
|---|---|
| user | `os.environ.get("USER", "unknown")` |
| version | `platform.python_version()` |
| implementation | `platform.python_implementation()` |
| system, release | `platform.system()`, `platform.release()` |
| machine | `platform.machine()` |
| folder | `os.getcwd()` |
| in venv | `sys.prefix != sys.base_prefix` |

Each border is 30 `=` signs. Note the `Python` line: the implementation is in
brackets with no space inside them.

**Quality rules (the tests check these too):**

1. The first line is the shebang `#!/usr/bin/env python3`.
2. The file has a **module docstring** (a string in triple quotes right after
   the shebang) describing what the script does.
3. Every variable name is `snake_case`.
4. No line is longer than 79 characters.

**Example** (your values will differ)

Input:
```
kav
```
Output:
```
==============================
System report for kav
==============================
User: asha
Python: 3.14.4 (CPython)
OS: Linux 6.8.0-45-generic
Machine: x86_64
Folder: /home/asha/code/sysinfo
In venv: True
==============================
```

When it passes, try the real thing: put it in its own folder with a venv and a
Git repository, `chmod +x` it, run `./sysinfo.py`, and commit it.
