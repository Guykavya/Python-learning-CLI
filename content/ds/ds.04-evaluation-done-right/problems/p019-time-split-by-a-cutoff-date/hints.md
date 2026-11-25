## Hint 1

One boolean mask does it. Which comparison puts a row that falls exactly on the cutoff into the test part?

## Hint 2

```text
cut = pd.Timestamp(cutoff) if the column holds dates else cutoff
mask = df[date_col] < cut
return df[mask], df[~mask]
```
