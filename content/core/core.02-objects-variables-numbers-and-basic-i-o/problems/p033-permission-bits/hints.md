## Hint 1

Write 6 in binary. Which bits are set? What does `6 & 4` give? And `6 & 1`?

## Hint 2

`&` with a mask tests a bit. `|` with a mask sets a bit. `& ~mask` clears a bit, because `~2` has every bit set except the 2s bit.

## Hint 3

```
print("Read:", (mode & 4) != 0)
print("Without write:", mode & ~2)
print("With execute:", mode | 1)
```
