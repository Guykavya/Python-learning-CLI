# Is it the same text?

Two strings can look identical but compare unequal, because `é` can be stored as one code point (`U+00E9`) or as `e` followed by a combining accent (`U+0301`). Read two lines and print:

```
Exact: <a == b>
Ignoring case: <a.casefold() == b.casefold()>
Normalised: <the two are equal after NFC normalisation and casefolding>
Lengths: <len(a)> <len(b)>
```

For the third line, compare `unicodedata.normalize("NFC", a).casefold()` with the same for `b`.

**Example**

Input (the second line is typed with a combining accent, `CAFE` + `U+0301`):
```
café
CAFÉ
```
Output:
```
Exact: False
Ignoring case: False
Normalised: True
Lengths: 4 5
```
