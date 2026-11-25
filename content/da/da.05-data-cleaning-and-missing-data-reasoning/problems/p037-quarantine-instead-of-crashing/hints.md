## Hint 1

What happens when you call `schema.validate(df, lazy=True)`, and what does the exception object carry? Which column of
`failure_cases` tells you whether a failure belongs to a row? How do you collect, per row label, all the column names
that failed? How do you pick rows of `df` by their labels, and the rest?

## Hint 2

```text
try: schema.validate(df, lazy=True)
except pa.errors.SchemaErrors as e:
    fc = e.failure_cases
    if some fc["index"] is missing:  raise            # not tied to a row
    why = fc.groupby("index")["column"] -> sorted unique names joined with ", "
    bad = df.index.isin(why.index)
    quarantine = df[bad] with reasons taken from why (same order as the rows)
    valid = df[~bad]
no exception: valid = copy of df, quarantine = empty frame with a 'reasons' column
```
