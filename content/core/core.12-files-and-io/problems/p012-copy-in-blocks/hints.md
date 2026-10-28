## Hint 1

`f.read(4)` reads at most 4 bytes. What does it return when the end of the file has been reached? How can a `while` loop use that?

## Hint 2

```
blocks = 0
open src "rb" and dst "wb"
while True:
    block = src.read(block_size)
    if not block: break
    dst.write(block)
    blocks += 1
return blocks
```
You can open two files in one `with`, separated by a comma.
