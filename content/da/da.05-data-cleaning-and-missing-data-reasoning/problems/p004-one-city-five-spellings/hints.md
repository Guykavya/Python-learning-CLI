## Hint 1

Which `str` methods remove spaces at both ends and dots at the end? How do you collapse two spaces into one (a regex
with `regex=True`)? What does `Series.map(dict)` return for a key that is not in the dict? Once you have the key and
the mapped value, how can you tell "had a key but no mapping" from "was missing already"?

## Hint 2

```text
key = s.str.strip().str.rstrip(".").str.strip().str.replace(r"\s+", " ", regex=True).str.casefold()
clean = key.map(mapping)                       # NaN where the key is not a mapping key
lost = key.notna() AND clean.isna()            # had text, got nothing
unmapped = sorted(set(key[lost]))
return clean, unmapped
```
