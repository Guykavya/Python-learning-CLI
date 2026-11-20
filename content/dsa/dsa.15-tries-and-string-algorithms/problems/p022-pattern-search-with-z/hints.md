## Hint 1

Let `m = len(pattern)` and `u = pattern + text`. For a text position `i`, `z[m + i]` is the common prefix of `u` and `u[m + i:] = text[i:]`. The first `m` characters of `u` are the pattern, so the first `min(z[m + i], m)` characters of that common prefix are a common prefix of `pattern` and `text[i:]`.

## Hint 2

If `z[m + i] >= m`, the whole pattern matches at `i`; anything beyond `m` is a comparison of the text with itself, which we ignore by taking `min(..., m)`. The match always stays inside the text because `u[m + i:]` is a suffix of `text`. So no separator is needed: only the cap.

## Hint 3

```
m = len(pattern)
z = z_function(pattern + text)
lengths = [min(z[m + i], m) for i in range(len(text))]
positions = [i for i, L in enumerate(lengths) if L == m]
```

Handle `m == 0` separately for `z_search` (also the position `len(text)`).
