# What does lazy validation report?

Chapter section 11.2. Eager validation stops at the first failure and raises `SchemaError`. Lazy validation
(`lazy=True`) collects every failure and raises `SchemaErrors`, whose `failure_cases` is an ordinary DataFrame with one
row per failing cell. Read the program, hand-trace it, and write **every line it prints**, in order, in `answer.txt`.

```python
import numpy as np
import pandas as pd
import pandera.pandas as pa

schema = pa.DataFrameSchema({
    "id": pa.Column(int, unique=True),
    "age": pa.Column(float, pa.Check.in_range(18, 75), nullable=True),
    "city": pa.Column(str, pa.Check.isin(["Pune", "Delhi"])),
})
df = pd.DataFrame({"id": [1, 2, 2, 4],
                   "age": [20.0, 80.0, np.nan, 17.0],
                   "city": ["Pune", "Goa", "Delhi", "Pune"]})

try:
    schema.validate(df)
except pa.errors.SchemaError as e:
    print(type(e).__name__)

try:
    schema.validate(df, lazy=True)
except pa.errors.SchemaErrors as e:
    fc = e.failure_cases
    print(type(e).__name__, len(fc))
    print(sorted(set(zip(fc["column"], fc["check"].astype(str)))))
    print({c: sorted(g["index"].tolist()) for c, g in fc.groupby("column")})
```

Facts you can rely on (pandera 0.36, measured): a unique column reports **every** row that takes part in a repeated
value, with the check name `field_uniqueness`; `Check.in_range(18, 75)` prints as `in_range(18, 75)`;
`Check.isin(["Pune", "Delhi"])` prints as `isin(['Pune', 'Delhi'])`. A missing value in a `nullable=True` column is
not a failure.

Write the lines exactly as Python prints them. Do not run the code before you have written your answer.

## Example

For a table with one bad age, `{c: sorted(g["index"].tolist()) for c, g in fc.groupby("column")}` prints
`{'age': [3]}` when the failing row has label 3.

## After you answer

- Why is the second number 5 and not 4 (the number of rows) or 3 (the number of columns with a problem)?
- Why does the missing age of row 2 not appear anywhere?
- Which rows would the eager version have reported, and how many?
