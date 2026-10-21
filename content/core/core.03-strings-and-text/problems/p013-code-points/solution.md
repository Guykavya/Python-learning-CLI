## Code

```python
ch = input()
code = ord(ch)
print(f"Code point: {code}")
print(f"Unicode: U+{code:04X}")
print(f"Next: {chr(code + 1)}")
```

## Why `04X` and not `4X`

Without the `0`, the padding would be spaces: `U+  41`. With `0` it is `U+0041`. Code points above `FFFF` simply use more digits, so `04X` is a minimum.

## Another way

`hex(code)` gives `'0x41'`, which you would then have to slice and uppercase. The format spec does it all at once.
