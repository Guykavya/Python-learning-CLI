# Run a command safely: an argument list, never `shell=True`

A program wants to run a helper script with a name typed by the user. The tempting version builds
one string and lets the shell run it:

```python
import subprocess, sys

def greet_unsafe(name):
    cmd = f'"{sys.executable}" greet.py {name}'
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

def greet_safe(name):
    return subprocess.run([sys.executable, "greet.py", name], capture_output=True, text=True).stdout
```

`greet.py` prints `"Hello,"` and its arguments joined with `" | "`, so you can see exactly what
arrived. Real output on Linux (`splitlines()` of each result):

```text
'Asha'
  unsafe: ['Hello, Asha']
  safe:   ['Hello, Asha']
'Asha Rao'
  unsafe: ['Hello, Asha | Rao']
  safe:   ['Hello, Asha Rao']
'Asha; echo HACKED'
  unsafe: ['Hello, Asha', 'HACKED']
  safe:   ['Hello, Asha; echo HACKED']
'$(whoami)'
  unsafe: ['Hello, you']             <- your own user name (shown here as 'you'): the shell ran whoami
  safe:   ['Hello, $(whoami)']
```

With `shell=True` the **shell** reads the string: a space splits the name in two, `;` starts a second
command, `$( )` runs a command and pastes its output. If the user types `x; rm -rf ~` instead of
`echo HACKED`, your program deletes their home folder. This is **shell injection**. On Windows `cmd.exe`
does the same with `&`, `|` and `%VAR%`.

(Even without an attacker the string version is fragile: without the quotes around
`sys.executable`, a Python installed in a folder with a space, like `learning module/.venv`, does not
start at all: `/bin/sh: .../learning: not found`.)

With a **list**, no shell is involved: Python starts the program directly and each list item arrives
as exactly one argument, whatever characters it contains.

## Your task

Write two functions in `solution.py`:

1. `build_command(script, args) -> list[str]` returns `[sys.executable, str(script), *args]`.
   `script` is a `str` or a `Path`; `args` is any sequence of strings. If any argument is not a
   `str`, raise `TypeError` (programs receive text, so convert numbers yourself before calling).
2. `run_script(script, args, timeout=10.0) -> str` runs that command with `subprocess.run`
   **without a shell**, captures the output as text and returns `stdout`.
   - Pass `timeout=timeout` so a stuck helper cannot hang your program.
   - Use `check=True`: a helper that exits with a non-zero code must raise
     `subprocess.CalledProcessError`.

Use `import subprocess` and call `subprocess.run(...)` (the tests watch that call).

**Example**

```python
# echo_args.py contains:  import json, sys; print(json.dumps(sys.argv[1:]))
build_command("echo_args.py", ["a b", "c"])
# ['/path/to/python', 'echo_args.py', 'a b', 'c']

run_script("echo_args.py", ["Asha; echo HACKED", "$(whoami)"])
# '["Asha; echo HACKED", "$(whoami)"]\n'     each item arrived unchanged
```
