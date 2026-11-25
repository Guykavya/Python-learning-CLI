## Approach

Column rules go inside each `Column`, relations between columns go to `checks=` as functions of the whole frame. "If
student then under 30" is the logical implication `not student or age < 30`, which is `~d["student"] | (d["age"] < 30)`.
Row labels come back in `failure_cases["index"]`, one row per failing cell (a relation is reported for the columns it
involves), so the test collects the **set** of labels.

## Code

```python
import pandera.pandas as pa

SCHEMA = pa.DataFrameSchema(
    {
        "user_id": pa.Column(int, unique=True),
        "signup": pa.Column("datetime64[ns]", coerce=True),
        "last_seen": pa.Column("datetime64[ns]", coerce=True),
        "age": pa.Column(int, pa.Check.in_range(13, 100)),
        "student": pa.Column(bool),
    },
    checks=[
        pa.Check(lambda d: d["last_seen"] >= d["signup"], error="last_seen is before signup"),
        pa.Check(lambda d: ~d["student"] | (d["age"] < 30), error="a student must be under 30"),
    ],
)
```

## Complexity

O(rows) per check: one vectorised comparison each.

## Another way

With the class style, a method decorated with `@pa.dataframe_check` is the same thing. A third way: a
`pa.Check(..., element_wise=True)` per row is slower and unnecessary here. Always add `error="..."`: it becomes the
message in the report (the tests do not read it, a human colleague will).
