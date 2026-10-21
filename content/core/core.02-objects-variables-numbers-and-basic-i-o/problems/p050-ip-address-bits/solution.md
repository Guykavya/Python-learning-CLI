## Approach

Shifting left by 8 multiplies by 256 and makes room for one more byte. Shifting right by 8 divides
by 256 (floor). `& 255` keeps only the lowest byte.

## Code

```python
a = int(input())
b = int(input())
c = int(input())
d = int(input())
x = int(input())
n = (a << 24) | (b << 16) | (c << 8) | d
print("Integer:", n)
print("Hex:", hex(n))
print(f"Address: {x >> 24 & 255}.{x >> 16 & 255}.{x >> 8 & 255}.{x & 255}")
```

## Why hex is handy

Each pair of hex digits is one byte: `0xc0a80101` is `c0 a8 01 01`, which is `192 168 1 1`.
That is why programmers like hex for bit patterns.

## Another way

Pure arithmetic: `n = a * 256**3 + b * 256**2 + c * 256 + d`, and
`x // 256**2 % 256` for an octet. `divmod(x, 256)` repeated four times also works.
Python's `ipaddress` module does all of this for real programs.
