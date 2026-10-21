# Am I in a virtual environment?

Write a script that reports which environment is running it:

```
Executable: /home/asha/code/.venv/bin/python
Prefix: /home/asha/code/.venv
Base prefix: /usr
In virtual environment: True
```

- `Executable` is `sys.executable`.
- `Prefix` is `sys.prefix`: the environment in use.
- `Base prefix` is `sys.base_prefix`: the installation the environment was
  built from.
- The last line is `True` inside a venv and `False` outside. Compute it from
  the two prefixes with `!=` ("is not equal to"). No `if` statement is needed:
  `print(5 != 3)` prints `True`.

The tests run your script **twice**: once with the venv's Python and once with
the base Python. The output must be right both times.

**Example**

Run with the system Python:
```bash
$ /usr/bin/python3 solution.py
Executable: /usr/bin/python3
Prefix: /usr
Base prefix: /usr
In virtual environment: False
```
