## Hint 1

Three problems, three steps, and they must run in a certain order: can you call `.str.strip()` on a column of
integers? For the match rate, which method answers "is this value somewhere in that other column?" for every row, and
what is the mean of a column of `True`/`False`?

## Hint 2

```text
before  = float(left[key].isin(right[key]).mean())            # raw keys
clean(s) = s.astype(str).str.strip().str.upper()
l2 = left.assign(**{key: clean(left[key])});  r2 = the same for right
found = l2[key].isin(r2[key])
after = float(found.mean())
unmatched = sorted(l2.loc[~found, key].unique())
```
