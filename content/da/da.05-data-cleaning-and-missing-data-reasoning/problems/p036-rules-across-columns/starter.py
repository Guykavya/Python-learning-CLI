import pandera.pandas as pa

SCHEMA = pa.DataFrameSchema(
    {
        "user_id": pa.Column(int, unique=True),
        "signup": pa.Column("datetime64[ns]", coerce=True),
        "last_seen": pa.Column("datetime64[ns]", coerce=True),
        "age": pa.Column(int, pa.Check.in_range(13, 100)),
        "student": pa.Column(bool),
    },
    # TODO: checks=[ ...two dataframe-level checks (see problem.md)... ]
)
