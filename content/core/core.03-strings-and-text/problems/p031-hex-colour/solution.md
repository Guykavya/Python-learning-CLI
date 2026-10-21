## Code

```python
code = input().strip().removeprefix("#")
r = int(code[0:2], 16)
g = int(code[2:4], 16)
b = int(code[4:6], 16)
print(f"rgb({r}, {g}, {b})")
print(f"#{r:02x}{g:02x}{b:02x}")
```

## Why `02x`

A value under 16, like 10, is one hex digit (`a`). Without padding, `#0a0b0c` would print as `#abc`, which means something different. `02x` always gives two digits.

## Another way

For the second line, `"#" + code.lower()` gives the same text. Going through the numbers proves the round trip works, and it is the way you would build a code from three numbers.
