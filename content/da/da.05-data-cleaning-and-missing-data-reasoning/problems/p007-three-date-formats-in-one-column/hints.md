## Hint 1

Which kinds of values can a pattern tell apart without ambiguity (hint: `2024-03-05` and `05/03/2024` look different
even though both contain 03 and 05)? After you picked the format by pattern, what does parsing with an explicit format
do when the date does not exist (30 February)? Where should that failure end up?

## Hint 2

```text
patterns = [(regex, strptime format), ... three of them]
for each value:
    missing -> NaT
    text = strip
    try each pattern in turn with a FULL match
        matched: try parse with that format; on ValueError the result stays NaT; stop looking
    result still NaT -> add text to bad
build the Series from the list (same index), return it with sorted(bad)
```
Column-wise: for each pattern, `m = s.str.strip().str.fullmatch(rx)` then `pd.to_datetime(s[m].str.strip(), format=fmt, errors="coerce")`.
