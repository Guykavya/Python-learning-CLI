## Hint 1

In the REPL, compare `sys.prefix` and `sys.base_prefix` once with
`.venv/bin/python` and once with `/usr/bin/python3`. What is different?

## Hint 2

`a != b` gives the value `True` or `False`. You can print it directly:
`print("Label:", a != b)`.

## Hint 3

```
import sys
print("Executable:", sys.executable)
print("Prefix:", sys.prefix)
print("Base prefix:", sys.base_prefix)
print("In virtual environment:", <prefix> != <base prefix>)
```
