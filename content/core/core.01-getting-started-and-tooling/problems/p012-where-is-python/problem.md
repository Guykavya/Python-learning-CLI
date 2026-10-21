# Where is my Python?

When something "works in the terminal but not in VS Code", the first question
is: *which* Python is running, and from which folder? Write a script that
answers it:

```
Executable: /usr/bin/python3
Version: 3.14.4
Implementation: CPython
System: Linux
Folder: /home/asha/code
```

Use:

| Line | Source |
|---|---|
| Executable | `sys.executable` |
| Version | `platform.python_version()` |
| Implementation | `platform.python_implementation()` |
| System | `platform.system()` |
| Folder | `os.getcwd()` (the current working directory) |

Each line is a label, a colon, one space, and the value. The tests run your
script with different interpreters and folders, so nothing may be typed in by
hand.

**Example**

Run inside a venv in `/home/asha/code`:
```
Executable: /home/asha/code/.venv/bin/python
Version: 3.14.4
Implementation: CPython
System: Linux
Folder: /home/asha/code
```
