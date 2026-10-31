## Hint 1

`subprocess.run(cmd_list, input=..., capture_output=True, text=True, timeout=...)` does all of
`run_python` in one call. Which attributes of the result do you return? Why is `text=True`
needed (try without it and look at the type of `stdout`)?

## Hint 2

For `run_or_raise`, reuse `run_python`. To find the last non-empty line of stderr:
`[l for l in err.splitlines() if l.strip()]` and take `[-1]`, unless the list is empty. For
`echo_args`, the extra arguments go into the **same list**, after the code:
`[sys.executable, "-c", code, *args]`.

## Hint 3

```
run_python:   proc = run([sys.executable, "-c", code], input=stdin_text,
                         capture_output=True, text=True, encoding="utf-8", timeout=10)
              return proc.returncode, proc.stdout, proc.stderr
run_or_raise: rc, out, err = run_python(code)
              if rc != 0: raise RuntimeError(last non-empty err line or f"exit code {rc}")
              return out
echo_args:    code = "import json, sys; print(json.dumps(sys.argv[1:]))"
              proc = run([sys.executable, "-c", code, *args], capture_output=True, text=True, timeout=10, check=True)
              return json.loads(proc.stdout)
```
