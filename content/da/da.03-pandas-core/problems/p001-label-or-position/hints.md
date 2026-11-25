## Hint 1

What are the labels of the example Series, and what are the positions? Which of `s[n]`, `s.loc[n]`, `s.iloc[n]` always means "the n-th row from the top", and which always means "the row named n"?

## Hint 2

```text
price_of(s, label): look up by NAME     -> s.loc[label]
nth_price(s, n):    look up by POSITION -> s.iloc[n]
wrap the result in float(...)
```
