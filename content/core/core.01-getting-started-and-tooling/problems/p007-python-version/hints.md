## Hint 1

Try `import sys` and then `sys.version_info` in the REPL. What does it show?

## Hint 2

`sys.version_info.major` is a number. `print("Major:", x)` prints a label, a
space, then the value. `platform.python_version()` returns text like `'3.14.4'`.

## Hint 3

```
print("Major:", sys.version_info.<major part>)
print("Minor:", sys.version_info.<minor part>)
print("Full:", platform.<function>())
```
