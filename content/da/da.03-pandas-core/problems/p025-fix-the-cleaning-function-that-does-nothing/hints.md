## Hint 1

Count the brackets on the left side of each `=`. In `df[mask]["qty"] = 0`, what does the first `[]` return, and where does the value `0` go? What is the same problem in `df["price"][i] = ...`? Also: what does the function do to the caller's frame?

## Hint 2

```text
out = df.copy()                                  # never touch the input
out.loc[out["qty"] < 0, "qty"] = 0               # ONE loc: rows, column, value
out["price"] = out["price"].round(2)             # whole column, no loop
return out
```
