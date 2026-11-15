## Hint 1

How many windows of length `L` are there, and how could you recognise a repeated one in O(1) without comparing letters?

## Hint 2

Keep the hash of the current window. To slide: remove the letter that leaves (weight `B^(L-1)`), multiply by `B`, add the entering letter, take `% M`. Put each hash in a set.

## Hint 3

```
h = hash of s[:L]; top = pow(B, L-1, M); hashes = {h}
for i in range(L, n):
    h = ((h - v(s[i-L]) * top) * B + v(s[i])) % M
    hashes.add(h)
print(len(hashes))
```
