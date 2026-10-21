# Split into chunks

Read a line of items, then a chunk size `k` (at least 1). Split the items into chunks of `k`
items; the last chunk may be shorter. Print each chunk as `<number>: <items>` (chunks numbered
from 1). For an empty line, print `No chunks`.

**Example**

Input:
```
a b c d e f g
3
```
Output:
```
1: a b c
2: d e f
3: g
```
