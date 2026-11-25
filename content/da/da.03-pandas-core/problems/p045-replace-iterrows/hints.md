## Hint 1

The loop does three things per row: choose a discount from `qty`, multiply, store. Which tools of section 15.3 choose a value per row from ordered conditions *for the whole column at once*? What must you remember about the **order** of the conditions?

## Hint 2

```text
rate  = np.select([qty >= 10, qty >= 5], [0.10, 0.05], default=0.0)    # first matching condition wins
total = qty * unit_price * (1 - rate)                                  # one vectorised multiplication
return pd.Series(total, index=df.index, name="total")
```
Put the narrowest condition (`>= 10`) first: `np.select` takes the first one that is true.
