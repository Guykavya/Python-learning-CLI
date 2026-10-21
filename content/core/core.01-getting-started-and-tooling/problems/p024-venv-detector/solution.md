## Approach

When Python starts, it looks for `pyvenv.cfg` near its executable. If found,
it sets `sys.prefix` to the venv folder while `sys.base_prefix` keeps pointing
to the real installation. Outside a venv both are the same.

## Code

```python
import sys

print("Executable:", sys.executable)
print("Prefix:", sys.prefix)
print("Base prefix:", sys.base_prefix)
print("In virtual environment:", sys.prefix != sys.base_prefix)
```

## Why not check the `VIRTUAL_ENV` variable?

`activate` sets the environment variable `VIRTUAL_ENV`, but running
`.venv/bin/python` directly does not. The script would then wrongly say
`False`. Comparing prefixes asks the interpreter itself, so it is always right.

## Another way

`"VIRTUAL_ENV" in os.environ` is a common shortcut in shell scripts, with the
weakness described above.
