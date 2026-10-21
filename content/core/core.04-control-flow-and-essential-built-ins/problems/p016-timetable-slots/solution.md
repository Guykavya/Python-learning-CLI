## Approach

Convert to minutes, let `range` produce slot starts, convert back for printing.

## Code

```python
start_text = input().strip()
end_text = input().strip()
length = int(input())

start = int(start_text[:2]) * 60 + int(start_text[3:])
end = int(end_text[:2]) * 60 + int(end_text[3:])

if length <= 0:
    print("invalid length")
else:
    found = False
    for s in range(start, end - length + 1, length):
        h1, m1 = divmod(s, 60)
        h2, m2 = divmod(s + length, 60)
        print(f"{h1:02d}:{m1:02d}-{h2:02d}:{m2:02d}")
        found = True
    if not found:
        print("No slots")
```

## Why `end - length + 1`

A slot starting at `s` fits when `s + length <= end`, that is `s <= end - length`. `range`
excludes its stop, so the stop is `end - length + 1`. Test with a slot that ends exactly at
closing time.

## Another way

Build the range first and test it: `slots = range(...)`, then `if not slots: print("No slots")`.
An empty range is falsy.
