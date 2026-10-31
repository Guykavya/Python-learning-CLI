## Hint 1

What does `f.seek(0, 2)` do, and what does `f.tell()` then return? If you know the position `pos`, where must you
`seek` to read the block that ends at `pos`? How do you know that you have enough lines?

## Hint 2

```
open "rb"; seek to end; pos = size; data = b""
while pos > 0 and data.count(b"\n") <= n:
    step = min(block_size, pos)
    pos -= step
    seek(pos); data = read(step) + data      # new block goes in FRONT
lines = data.split(b"\n")
drop the last item if it is empty (the final newline)
take the last n, strip a trailing b"\r", decode
```
Why `<= n` and not `< n`? The first line you keep must be complete, so you need one newline **before** it.
