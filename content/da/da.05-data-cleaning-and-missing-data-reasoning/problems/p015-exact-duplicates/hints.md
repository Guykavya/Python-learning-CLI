## Hint 1

Which method returns a Boolean Series that is `True` for rows repeating an earlier row? What does its `keep` argument
decide? How do you select the rows where a mask is **not** true, and how do you count the `True`s of a mask?

## Hint 2

```text
repeat = df.duplicated(keep="first")      # True for every repeat after the first copy
clean = df[~repeat]                        # keep the others, original labels
n_removed = int(repeat.sum())
return clean, n_removed
```
`df.drop_duplicates()` gives the same `clean`, but then you must compute the count from the lengths.
