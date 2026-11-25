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
