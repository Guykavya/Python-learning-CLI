## Hint 1

How do you say "this column is a float between two bounds" in pandera, and what must you add to allow missing values?
Which argument of `Column` makes a column unique, and which `Check` tests that text contains a character? What does
`strict=False` allow?

## Hint 2

```text
pa.DataFrameSchema({
    "resp_id":      pa.Column(int, unique=True),
    "age":          pa.Column(float, pa.Check.in_range(18, 75), nullable=True),
    "city":         pa.Column(str, pa.Check.isin([...])),
    "income":       pa.Column(float, pa.Check.in_range(1000, 1_000_000), nullable=True),
    "satisfaction": pa.Column(int, pa.Check.in_range(1, 10)),
    "email":        pa.Column(str, pa.Check.str_contains("@"), nullable=True),
}, strict=False)
```
