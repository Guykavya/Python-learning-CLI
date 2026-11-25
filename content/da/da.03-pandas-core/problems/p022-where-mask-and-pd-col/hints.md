## Hint 1

If you filter with `df[...]`, what happens to the rows you do not keep? Which method replaces values *where a condition is True* and keeps everything else? What does a comparison with a missing value give?

## Hint 2

```text
too_big = df["discount"] > cap          # False for NaN: it is never "too big"
new_discount = df["discount"].mask(too_big, cap)
return df.assign(discount=new_discount)          # a new frame, other columns unchanged
```
`where(df["discount"] <= cap, cap)` is the same idea written the other way round (careful: it would also replace NaN).
