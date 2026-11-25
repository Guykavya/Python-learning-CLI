## Approach

Two layers. First the **cheap, safe** normalisation (strip, trailing dots, one space, case) turns a hundred ways of
typing a city into a small set of keys. Second a **mapping table** says which keys are the same city, including the
typos. Typos are never guessed by code: the table is explicit, reviewable, and reusable next month. Whatever the table
does not know is *not* guessed either; it becomes missing and its key is reported, so you extend the table and run
again. After the table is complete, `unmapped == []`.

## Code

```python
import pandas as pd


def standardise_city(s, mapping):
    key = (s.str.strip().str.rstrip(".").str.strip()
            .str.replace(r"\s+", " ", regex=True).str.casefold())
    clean = key.map(mapping)
    unmapped = sorted(set(key[key.notna() & clean.isna()]))
    return clean, unmapped
```

## Complexity

O(n) string passes plus a hash lookup per value. For a column with few distinct values you can normalise and map only
the unique values and map back (chapter 4.5).

## Another way

`s.str.strip().str.rstrip(".").str.title().replace(CITY_FIX)` is the chapter's version: it keeps the title case as the
official form and uses `replace` for the typos. The key version here is a little more general (the mapping decides the
final spelling, so `"new delhi"` can map to `"Delhi"`), and it makes the leftover list easy to compute.
