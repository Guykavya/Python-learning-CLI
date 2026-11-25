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
