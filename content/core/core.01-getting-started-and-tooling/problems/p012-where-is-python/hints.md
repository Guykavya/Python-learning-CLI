## Hint 1

Try each source in the REPL first: `import sys`, then `sys.executable`; `import
platform`, then `platform.system()`. Which ones need brackets?

## Hint 2

`sys.executable` is a value (no brackets). The `platform` functions and
`os.getcwd` are functions and need `()`. `print("Label:", value)` gives
`Label: value`.

## Hint 3

```
print("Executable:", sys.executable)
print("Version:", platform.python_version())
... Implementation, System ...
print("Folder:", os.getcwd())
```
