## Hint 1

`s.map(dict)` replaces every code by its name and gives `NaN` for a key that is not in the dictionary (section 15.2). But a code that was *already* missing also comes out as `NaN`. How can you tell the two cases apart?

## Hint 2

```text
mapped     = s.map(mapping)
is_unknown = s is not missing  AND  mapped is missing
names      = mapped, with "Other" where is_unknown
unknown    = sorted distinct values of s[is_unknown]
```
Use `mapped.where(~is_unknown, "Other")` (keep where *not* unknown, else "Other"), and `.unique().tolist()` before `sorted`.
