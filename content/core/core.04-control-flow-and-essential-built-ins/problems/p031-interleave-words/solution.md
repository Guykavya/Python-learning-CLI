## Approach

`zip` handles the part where both lines have characters. Slicing picks up whatever is left
in the longer line.

## Code

```python
a = input()
b = input()
result = ""
for x, y in zip(a, b):
    result += x + y
result += a[len(b):] + b[len(a):]
print(result if result else "(empty)")
```

## Why the leftover slice works

If `a` is longer, `a[len(b):]` is its unused tail and `b[len(a):]` starts past the end of `b`,
which gives `""` (slicing never raises an error). If `b` is longer, the opposite. If they are
equal, both are empty.

## Another way

Loop over `range(max(len(a), len(b)))` and add `a[i]` when `i < len(a)`, and `b[i]` when
`i < len(b)`. It works but has more conditions to get wrong.
