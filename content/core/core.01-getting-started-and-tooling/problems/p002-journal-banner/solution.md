## Approach

Build the border once with string repetition, keep it in a variable, and print
it before and after the title.

## Code

```python
border = "=" * 30
print(border)
print("   PYTHON LEARNING JOURNAL")
print(border)
print("Day 1: Getting started")
```

## Why

`"=" * 30` creates a new string made of 30 copies of `"="`. Using a variable
means the two borders can never disagree, and changing the width later is a
one-character edit.

## Another way

`print("=" * 30)` twice, without a variable. It is fine, but repeating the same
expression is exactly what a variable is for.
