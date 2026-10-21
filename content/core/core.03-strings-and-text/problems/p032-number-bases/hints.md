## Hint 1

Section 17 shows the type letters for other bases. Which symbol adds the prefix?

## Hint 2

`b`, `o`, `x` are the types. `#` adds `0b`, `0o`, `0x`. `08b` pads to 8 digits with zeros. `_b` groups binary digits in fours.

## Hint 3

```
n = int(input())
print(f"bin: {n:b}")
print(f"oct: {n:o}")
print(f"hex: {n:x}")
print(f"prefixed: {n:#b} {n:#o} {n:#x}")
print(f"byte: {n:08b}")
print(f"grouped: {n:_b}")
```
