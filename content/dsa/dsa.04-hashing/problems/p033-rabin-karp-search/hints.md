## Hint 1

Comparing `p` with the slice `t[i:i+m]` for every `i` costs `O(n * m)`. What if you compared two numbers first?

## Hint 2

Hash `p` and the first window. To move one step right, remove the hash contribution of the letter that leaves (it was multiplied by `B^(m-1)`), shift everything by multiplying by `B`, and add the new letter.

## Hint 3

```
hp = hash(p); h = hash(t[:m]); top = pow(B, m-1, M)
for i in range(n-m+1):
    if h == hp and t[i:i+m] == p: record i
    if i+m < n: h = ((h - v(t[i])*top) * B + v(t[i+m])) % M
```
