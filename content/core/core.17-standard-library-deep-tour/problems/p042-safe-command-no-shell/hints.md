## Hint 1

What does a shell do with the text `Asha; echo HACKED` that a program started directly does not?
If you give `subprocess.run` a **list**, who decides where one argument ends and the next starts?

## Hint 2

`build_command` is one line after a check: loop over `args`, `raise TypeError` if `isinstance(arg, str)`
is false, then return `[sys.executable, str(script), *args]`. In `run_script`, call `subprocess.run`
with that list and the keyword arguments `capture_output=True`, `text=True`, `check=True`, `timeout=timeout`.

## Hint 3

```
build_command(script, args):
    for arg in args: if not a str -> raise TypeError
    return [sys.executable, str(script)] + list(args)

run_script(script, args, timeout):
    result = subprocess.run(build_command(script, args),
                            capture_output=True, text=True, check=True, timeout=timeout)
    return result.stdout
```
