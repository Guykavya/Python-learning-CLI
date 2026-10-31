# Run a child process and capture its output

`subprocess.run([...])` starts another program, waits for it, and gives you a
`CompletedProcess` with `returncode`, `stdout` and `stderr`. To keep everything portable
(Linux, macOS **and** Windows) the child here is always Python itself:
`[sys.executable, "-c", code]`. `sys.executable` is the full path of the Python running your
code, so the child has the same version and packages. Never use shell commands like `ls` or
`echo`, and never `shell=True`.

Write in `solution.py`:

1. `run_python(code, stdin_text="") -> tuple[int, str, str]`: run `code` in a child Python,
   send `stdin_text` to its standard input, and return `(returncode, stdout, stderr)` as **text**.
   A failing child is not an error for this function: just report its exit code.
2. `run_or_raise(code) -> str`: like `run_python`, but return only stdout; if the exit code is not
   0, raise `RuntimeError` whose message is the **last non-empty line** of stderr (for a crash that
   is the line naming the exception). If stderr is empty, mention the exit code in the message.
3. `echo_args(args) -> list[str]`: start a child Python with `args` as extra command-line
   arguments; the child prints `json.dumps(sys.argv[1:])`; return what it received
   (`json.loads` its stdout). This shows that a **list** of arguments arrives unchanged.

Rules: pass `timeout=` (10 seconds is plenty) to every `subprocess.run`, use `text=True`, and
pass `input=` so the child never waits for the keyboard.

**Example**

```python
run_python("print('hello')")                        # (0, 'hello\n', '')
run_python("import sys; print(sys.stdin.read().upper())", "abc")   # (0, 'ABC\n', '')
run_python("import sys; sys.exit(3)")                # (3, '', '')
run_or_raise("1 / 0")       # RuntimeError: ZeroDivisionError: division by zero
echo_args(["two words", "x; echo hacked"])          # ['two words', 'x; echo hacked']
```
