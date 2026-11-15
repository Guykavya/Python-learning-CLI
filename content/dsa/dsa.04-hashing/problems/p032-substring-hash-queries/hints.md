## Hint 1

Why is `H(s[l..r])` related to two prefix hashes? What did `P[r]` get multiplied by for the letters before position `l`?

## Hint 2

`P[r]` contains the first `l - 1` letters shifted left by `r - l + 1` places (multiplied by `B^(r-l+1)`). Subtract exactly that part: `P[l-1] * B^(r-l+1)`.

## Hint 3

```
P[0] = 0; pw[0] = 1
for each letter: P.append((P[-1]*B + v) % M); pw.append(pw[-1]*B % M)
query: (P[r] - P[l-1] * pw[r-l+1]) % M
```
