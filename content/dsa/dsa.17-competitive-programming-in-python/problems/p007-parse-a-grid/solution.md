## Approach

```python
import sys

data = sys.stdin.read().split()
n, m = int(data[0]), int(data[1])
rows = data[2:2 + n]
sr = sc = er = ec = 0
walls = 0
for r, row in enumerate(rows, 1):
    walls += row.count("#")
    c = row.find("S")
    if c != -1:
        sr, sc = r, c + 1
    c = row.find("E")
    if c != -1:
        er, ec = r, c + 1
print(sr, sc, er, ec, walls)
```

Because the rows contain no spaces, tokens are rows. The `\r` of a Windows file is whitespace, so `split` strips it. `find`, `count` run in C: they scan each row in C, where a Python double loop over every cell is much slower.

Example: rows `#..S`, `.#..`, `E..#`: `S` is in row 1 at index 3, so column 4; `E` is in row 3 at index 0, so column 1; the counts 1 + 1 + 1 give 3 walls.

## Complexity

`O(n * m)` characters, mostly in C.

## Another way

`sys.stdin.readline()` per row (with `.rstrip()`), or reading bytes (`sys.stdin.buffer.read().split()`) and comparing with `b"#"`. Bytes are faster still, but you must remember that indexing gives integers.
