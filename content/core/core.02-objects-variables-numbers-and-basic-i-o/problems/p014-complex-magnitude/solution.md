## Approach

`complex(a, b)` builds `a + bj`. Python writes the imaginary unit as `j`, as engineers do.

## Code

```python
a = float(input())
b = float(input())
z = complex(a, b)
print(z)
print(f"|z| = {abs(z):.3f}")
print(z.conjugate())
```

## Why the printed form varies

When the real part is zero, Python prints just the imaginary part: `complex(0, 2)` prints `2j`.
Otherwise it prints both in brackets: `(3+4j)`. Both parts are always stored as floats.

## Another way

`z = a + b * 1j` gives the same value. You can read the parts back with `z.real` and `z.imag`.
