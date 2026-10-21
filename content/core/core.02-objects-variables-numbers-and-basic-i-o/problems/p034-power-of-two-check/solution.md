## Approach

Use the binary shape of the number instead of repeated division.

## Code

```python
n = int(input())
print((n & (n - 1)) == 0)
print(n.bit_length())
print(1 << (n.bit_length() - 1))
```

## Why it works

- `8 = 0b1000`, `7 = 0b0111`, `8 & 7 = 0`. For `6 = 0b110`, `5 = 0b101`, `6 & 5 = 0b100 = 4`, not 0.
- `bit_length()` is the position of the highest 1 bit, counting from 1. For 40 (`0b101000`) it is 6.
- The highest bit alone is `1 << (bit_length - 1)`, which is the largest power of two not above `n`.

All of this works on huge ints, because Python ints have no fixed size.

## Another way

`bin(n).count("1") == 1` also tests for a power of two, but it uses a string method (core.03)
and builds a string, which is slower for huge numbers.
