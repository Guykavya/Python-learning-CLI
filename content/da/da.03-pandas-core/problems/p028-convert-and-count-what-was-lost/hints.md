## Hint 1

What does `to_numeric(..., errors="coerce")` give for text it cannot read? How can you find the entries that became missing *and* were not empty or missing before? What would you do to the text first so that `" 3.5 "` works?

## Hint 2

```text
text    = s.str.strip()
numbers = pd.to_numeric(text, errors="coerce")
lost    = numbers.isna() & text.notna() & (text != "")      # was something, became nothing
bad     = sorted(text[lost].unique().tolist())
return numbers, bad
```
