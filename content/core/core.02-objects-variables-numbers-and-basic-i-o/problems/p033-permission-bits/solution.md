## Approach

Treat the number as a row of switches. Masks pick which switch to look at or change.

## Code

```python
mode = int(input())
print("Binary:", bin(mode))
print("Read:", (mode & 4) != 0)
print("Write:", (mode & 2) != 0)
print("Execute:", (mode & 1) != 0)
print("Without write:", mode & ~2)
print("With execute:", mode | 1)
```

## Why not + and -

Bit operations are safe whatever the current state. `5 - 2` is `3` (execute + write), which turns
write **on** for a mode that never had it. `5 & ~2` is `5`, correct. Likewise `7 + 1` is `8`, but `7 | 1` is `7`.

## Note on `~`

`~2` is `-3`. In Python, `~x` is `-x - 1`, because ints behave like an infinite row of bits in
two's complement. `-3` is `...11111101`: every bit set except the 2s bit, which is exactly the mask we want.

## Another way

`bool(mode & 4)` also converts the test to a bool.
