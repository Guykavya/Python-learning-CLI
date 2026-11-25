## Approach

1. Eager validation raises the **first** failure as `SchemaError`: `SchemaError`.
2. Lazy validation raises `SchemaErrors`. Count the failing cells:
   - `id`: the value 2 appears in rows 1 and 2, and uniqueness reports **both** rows: 2 cases;
   - `age`: 80 (row 1) and 17 (row 3): 2 cases; the missing age (row 2) is allowed by `nullable=True`;
   - `city`: `"Goa"` (row 1): 1 case.
   Total 5, so the line is `SchemaErrors 5`.
3. The sorted set of `(column, check)` pairs has three entries, sorted by column name:
   `('age', 'in_range(18, 75)')`, `('city', "isin(['Pune', 'Delhi'])")`, `('id', 'field_uniqueness')`.
   Note the quotes: the `isin` text contains single quotes, so Python prints that string in double quotes.
4. The failing row labels per column, sorted: `{'age': [1, 3], 'city': [1], 'id': [1, 2]}`.

## Output

```text
SchemaError
SchemaErrors 5
[('age', 'in_range(18, 75)'), ('city', "isin(['Pune', 'Delhi'])"), ('id', 'field_uniqueness')]
{'age': [1, 3], 'city': [1], 'id': [1, 2]}
```

(Hand-traced first, then run on pandas 3.1.1 with pandera 0.36.0: both agree.)

**Maintenance note.** The `check` text comes from pandera and has changed between versions (older versions printed
other forms of the same names). **When pandera is upgraded, re-run this program and replace `expected.txt` if the
text changed.** That is why the other pandera problems of this module compare column names and row labels, never this
text.

## Another way

Print `fc[["column", "check", "failure_case", "index"]].to_string(index=False)` to see the whole table. It is the
quickest way to understand what the report contains, but its layout depends on the terminal width, which is why this
problem prints only sorted pairs and dictionaries.
