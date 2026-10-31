# Copy a file in blocks

Write `copy_blocks(src, dst, block_size)` in `solution.py`. It copies the file `src` to `dst` in **binary
mode**, never holding more than `block_size` bytes in memory at once.

- The copy must be byte for byte identical. The data can be any bytes, not only text.
- Replace `dst` if it exists.
- Return the number of blocks that were read and written (an empty file gives 0).
- Every block except the last has exactly `block_size` bytes.

**Example**

```python
# src has 10 bytes
copy_blocks("src.bin", "dst.bin", 4)   # reads 4 + 4 + 2 bytes, returns 3
```
