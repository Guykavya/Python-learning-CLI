## Approach

Open both files in binary mode (`"rb"` and `"wb"`) in one `with` statement. Loop: read `block_size` bytes; an empty `bytes` object means end of file, so stop; otherwise write the block and count it. Memory use stays at one block.

## Code

```python
def copy_blocks(src, dst, block_size):
    blocks = 0
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        while True:
            block = fin.read(block_size)
            if not block:
                break
            fout.write(block)
            blocks += 1
    return blocks
```

## Complexity

O(n) time for n bytes, O(block_size) memory.

## Another way

`shutil.copyfileobj(src, dst, block_size)` does exactly this loop. `shutil.copyfile(src, dst)` copies a whole file in one call. Writing the loop once is how you learn what they do inside.
