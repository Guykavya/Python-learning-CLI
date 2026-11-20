## Hint 1

Keep a Fenwick tree of **counts** per value, plus a list of counts for the existence check in `remove`. The `k`-th smallest is the first value `v` with `prefix(v + 1) >= k`.

## Hint 2

Descent (chapter section 13): start with `pos = 0` and `pw` = the largest power of two `<= m`. For each `pw` from large to small: if `pos + pw <= m` and `t[pos + pw] < k`, the whole block `pos + 1 .. pos + pw` holds fewer than `k` items: skip it (`pos += pw`, `k -= t[pos]`). At the end the answer is `pos` (0-indexed).

## Hint 3

```
if k < 1 or k > size: return -1
pos, pw = 0, 1 << (m.bit_length() - 1)
while pw:
    nxt = pos + pw
    if nxt <= m and t[nxt] < k: pos = nxt; k -= t[nxt]
    pw >>= 1
return pos
```
