## Hint 1

Remove the front letter's term, shift, add the new letter:
`h = ((h - ord(text[i]) * top) * B + ord(text[i + m])) % M` with `top = pow(B, m - 1, M)`, computed once. Python's `%` always returns a value in `0 .. M - 1`, even when the left side is negative.

## Hint 2

For several pairs, compute `window_hashes` for each pair, and the pattern's hash for each pair. Position `i` is a candidate when **all** pairs agree. Equal strings always have equal hashes, so real matches are never lost; different strings must collide in every pair at once to slip through.

## Hint 3

```
lists = [window_hashes(text, m, B, M) for B, M in params]
wanted = [direct hash of pattern for B, M in params]
for i in range(len(text) - m + 1):
    if all(lists[j][i] == wanted[j] for j in range(len(params))):
        if not verify or text[i:i + m] == pattern: found.append(i)
```
