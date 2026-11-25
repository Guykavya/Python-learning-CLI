## Hint 1

Section 14.1 has the three verbs: `rename` (it accepts a function that is applied to every column name), `drop`, and `assign`. In which order must they run, if "starts with `tmp_`" is about the *new* names?

## Hint 2

```text
def snake(name): strip, lower, replace " " with "_"

df.rename(columns=snake)                                  # new names first
  .loc[:, lambda d: ~d.columns.str.startswith("tmp_")]    # keep the columns that do NOT start with tmp_
  .assign(revenue=lambda d: d["qty"] * d["unit_price"])   # lambda sees the frame built so far
```
`drop(columns=[...])` also works if you first compute the list of names to drop.
