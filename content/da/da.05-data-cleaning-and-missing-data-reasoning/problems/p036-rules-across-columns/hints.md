## Hint 1

Which argument of `DataFrameSchema` takes checks that look at the whole table? What does such a check receive and
return? How do you write "if A then B" as a Boolean expression (hint: it is false only when A is true and B is false)?
How do you compare two datetime columns row by row?

## Hint 2

```text
columns: user_id int unique; signup / last_seen: pa.Column("datetime64[ns]", coerce=True);
         age int in_range(13, 100); student bool
checks=[
    pa.Check(lambda d: d["last_seen"] >= d["signup"], error="..."),
    pa.Check(lambda d: ~d["student"] | (d["age"] < 30), error="..."),     # student implies age < 30
]
```
