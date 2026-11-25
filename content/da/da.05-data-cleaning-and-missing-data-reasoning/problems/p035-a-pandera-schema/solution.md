## Approach

Read the table of the problem as a sentence per column and translate each one: the type is the first argument of
`pa.Column`, the rules are `Check` objects, `nullable=True` allows missing values (the default is `False`, a good one:
missing values should be allowed on purpose), and `unique=True` forbids repeats. `Check.in_range` is inclusive by
default, which matches "from 18 to 75".

## Code

```python
import pandera.pandas as pa

SCHEMA = pa.DataFrameSchema(
    {
        "resp_id": pa.Column(int, unique=True),
        "age": pa.Column(float, pa.Check.in_range(18, 75), nullable=True),
        "city": pa.Column(str, pa.Check.isin(["Pune", "Delhi", "Mumbai"])),
        "income": pa.Column(float, pa.Check.in_range(1_000, 1_000_000), nullable=True),
        "satisfaction": pa.Column(int, pa.Check.in_range(1, 10)),
        "email": pa.Column(str, pa.Check.str_contains("@"), nullable=True),
    },
    strict=False,
)
```

## Complexity

Validation is O(rows x columns). Writing the schema costs nothing at run time.

## Another way

The class style: `class Survey(pa.DataFrameModel)` with `Series[int] = pa.Field(unique=True)` annotations and
`SCHEMA = Survey.to_schema()`. Both styles build the same schema object; use one of them everywhere in a project.
