## Approach

Lazy validation reports **every** failure at once. Each failure that belongs to a row has that row's label in
`failure_cases["index"]`; failures about the whole table have no label, and then there is nothing to quarantine, so
the exception is re-raised (the pipeline should stop: the file has the wrong shape). For labelled failures, group by
the label and join the sorted, unique column names into the reason. Then split the rows with `index.isin`.

## Code

```python
import pandas as pd
import pandera.pandas as pa


def split_valid(df, schema):
    try:
        schema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        fc = e.failure_cases
        if fc["index"].isna().any():
            raise
        why = fc.groupby("index")["column"].agg(lambda c: ", ".join(sorted(set(c.dropna()))))
        bad = df.index.isin(why.index)
        quarantine = df[bad].assign(reasons=why.reindex(df.index[bad]).to_numpy())
        return df[~bad].copy(), quarantine
    return df.copy(), df.iloc[0:0].assign(reasons=pd.Series(dtype="str"))
```

## Complexity

O(rows) for validation plus O(failures) for the grouping.

## Another way

`schema.validate(df, lazy=True)` with `drop_invalid_rows=True` removes bad rows for you, but writes no reason (the
chapter warns about it). Build the quarantine yourself, as here, so that each rejected row says why. In a real pipeline
you would also write the quarantine table to a file next to the log.
