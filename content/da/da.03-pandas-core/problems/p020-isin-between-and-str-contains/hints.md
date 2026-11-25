## Hint 1

Which Series method answers "is each value in this list?" Which one answers "is each value in this range, ends included?" Which `.str` method looks for a word, and which arguments control upper/lower case, missing values and pattern interpretation? How do you combine three masks?

## Hint 2

```text
mask = df["category"].isin(categories)
     & df["price"].between(lo, hi)                                       # inclusive by default
     & df["name"].str.contains(word, case=False, na=False, regex=False)
return df[mask]
```
