## Hint 1

Run `counts = np.zeros(3, dtype=int); counts[[0, 0, 1]] += 1` and look at `counts`. `counts[idx] += 1` is really three steps: read `counts[idx]`, add 1, write back. What do the two reads of position 0 see?

## Hint 2

```text
count_by_index: np.bincount(idx, minlength=n)       # counting small integers is exactly bincount's job
add_amounts:    out = totals.copy()
                np.add.at(out, idx, amounts)       # unbuffered: every duplicate is added
                return out
```
