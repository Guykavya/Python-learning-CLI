## Hint 1

Write the five rules as five pieces of one pattern, and use **`fullmatch`** on the stripped line
so nothing extra can hide before or after. Which pieces should be capturing groups (what do you
need afterwards)?

## Hint 2

Only two groups are needed: the letters and the digits. `str.zfill(4)` pads with zeros on the
left and leaves longer strings alone. A `set` remembers what you have already output.

```
ID_RE = ([A-Za-z]{2,4}) " *" [-_/]? " *" (\d{1,6})
for line in lines:
    m = ID_RE.fullmatch(line.strip())
    if not m: continue
    normal = prefix.upper() + "-" + digits.zfill(4)
    if normal not in seen: add to seen and result
```
