## Hint 1

Which built-in function makes a complex number from a real part and an imaginary part?

## Hint 2

`abs()` works on complex numbers too. For `3+4j` it gives `5.0`, the length sqrt(3*3 + 4*4).

## Hint 3

```
z = complex(a, b)
print(z)
print(f"|z| = {abs(z):.3f}")
print(z.conjugate())
```
