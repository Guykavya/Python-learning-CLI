## Approach

CSV keeps only text, so the CSV half is "what does `str()` give, and what does a string do
afterwards". Parquet keeps the schema, so the Parquet half is "which Python type matches each
column type".

| Line | Reasoning | Output |
|---|---|---|
| CSV data line | `str(7)`, `007` as is, `None` as empty, `str(Decimal("19.90"))`, `str(False)`, `str(datetime)` uses a space | `7,007,,19.90,False,2024-06-01 10:00:00+00:00` |
| `id` | DictReader returns text only | `id '7' str` |
| `city` | the empty field comes back as an empty string, not `None` | `city '' str` |
| `amount` | text, no longer a Decimal | `amount '19.90' str` |
| `paid` | the word `False` as text | `paid 'False' str` |
| `paid?` | `'False'` is a non-empty string, which is truthy | `paid? yes` |
| `back["id"] + back["zip"]` | `"7" + "007"` joins strings | `7007` |
| `num_columns, num_rows` | six fields, one row | `6 1` |
| `id` | int64 -> int | `id 7 int` |
| `zip` | a string column keeps the leading zeros | `zip '007' str` |
| `city` | a null in a string column is `None` | `city None NoneType` |
| `amount` | decimal128(8, 2) -> Decimal | `amount Decimal('19.90') Decimal` |
| `paid` | bool_ -> bool | `paid False bool` |
| `paid?` | real `False` is falsy | `paid? no` |
| arithmetic | `7 + 1`; `Decimal("19.90") * 2` keeps two places | `8 39.80` |
| `created_at` | aware datetime in UTC; same instant as the original | `2024-06-01T10:00:00+00:00 True` |
| types | pyarrow prints its own type names | `decimal128(8, 2) timestamp[us, tz=UTC]` |

## Full output

```
7,007,,19.90,False,2024-06-01 10:00:00+00:00
id '7' str
city '' str
amount '19.90' str
paid 'False' str
paid? yes
7007
6 1
id 7 int
zip '007' str
city None NoneType
amount Decimal('19.90') Decimal
paid False bool
paid? no
8 39.80
2024-06-01T10:00:00+00:00 True
decimal128(8, 2) timestamp[us, tz=UTC]
```

## Complexity

Not a performance question. The lesson is about information: CSV loses the types, so every
reader must parse them again (and every reader may parse them differently); Parquet stores them
once with the data.

## Another way

You can make a CSV round trip correct, but only with code on the reading side that knows the
schema: `int(back["id"])`, `back["city"] or None`, `Decimal(back["amount"])`,
`back["paid"] == "True"`, `datetime.fromisoformat(back["created_at"])`. That code is the schema,
written by hand and kept in sync with the writer. Parquet puts it into the file instead.
