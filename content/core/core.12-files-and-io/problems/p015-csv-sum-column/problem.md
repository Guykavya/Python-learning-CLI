# Sum a column of a CSV file

Write `sum_column(path, column)` in `solution.py`. It reads a UTF-8 CSV file that has a header row, and
returns the **sum of the numbers** in the column named `column`, as a `float`.

- Use the `csv` module. Fields can be quoted and can contain commas.
- A blank cell is skipped. Spaces around a number are fine (`" 12.5"`).
- If the column does not exist, let a `KeyError` happen.
- A file with only a header gives `0.0`.

**Example**

```text
name,amount
"Doe, Jane",10
Ravi, 2.5
Meera,
```

```python
sum_column("sales.csv", "amount")   # 12.5
```
