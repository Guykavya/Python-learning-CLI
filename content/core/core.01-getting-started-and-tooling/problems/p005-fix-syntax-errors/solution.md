## Approach

Python compiles the whole file before running it, so nothing prints while any
syntax error remains. Fix the reported error, rerun, read the next one.

## Code

```python
print("Welcome to Python")
print("Today we read tracebacks")
print("Fix one error at a time.")
```

## The three bugs

1. Line 1: the closing `)` is missing. Python reports `'(' was never closed`.
2. Line 2: the string opens with `'` and closes with `"`. A string ends only at
   the same quote type that started it, so it never ends.
3. Line 3: the closing `"` is missing, so `.)` became part of an endless string.

## Another way

`print('Today we read tracebacks')` with single quotes on both sides is equally
correct. Pick one style and use it consistently (PEP 8 does not prefer either).
