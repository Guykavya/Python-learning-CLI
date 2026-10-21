## Code

```python
n = int(input())
print(f"bin: {n:b}")
print(f"oct: {n:o}")
print(f"hex: {n:x}")
print(f"prefixed: {n:#b} {n:#o} {n:#x}")
print(f"byte: {n:08b}")
print(f"grouped: {n:_b}")
```

## Notes

- Width is a minimum, so `08b` on a number needing 9 digits shows all 9.
- With `_` and `b`, `o` or `x`, grouping is every 4 digits, counted from the right.

## Another way

`bin(n)`, `oct(n)` and `hex(n)` give the prefixed forms as strings. `bin(n)[2:]` removes the prefix. The format spec does all of it in one consistent way.
