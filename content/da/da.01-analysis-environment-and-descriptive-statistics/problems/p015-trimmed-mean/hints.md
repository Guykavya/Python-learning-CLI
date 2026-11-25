## Hint 1

What must you do to the data before cutting the ends? Which list slice drops `k` items from the front and `k` from the back (and what if `k` is 0)?

## Hint 2

```text
validate proportion and emptiness
k = math.floor(len(values) * proportion)
s = sorted(values)
kept = s[k : len(s) - k]
return sum(kept) / len(kept)
```
Careful: `s[k:-k]` is empty when `k == 0`.
