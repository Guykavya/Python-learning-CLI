# Write rows to a CSV file

Write `write_rows(path, header, rows)` in `solution.py`.

- `header` is a list of column names. `rows` is a list of lists with strings and numbers.
- Write a valid UTF-8 CSV file with the header first, then the rows. Replace an existing file.
- Use the `csv` module so that fields with commas, quotes or line breaks are quoted correctly.
- Open the file so that no extra blank lines or `\r\r\n` appear on any system (`newline=""`).
- Return the number of **data rows** written (not counting the header).

**Example**

```python
write_rows("out.csv", ["name", "note"], [["Doe, Jane", 'said "hi"'], ["Ravi", 2]])
# out.csv:
# name,note
# "Doe, Jane","said ""hi"""
# Ravi,2
```
(The csv module ends each line with `\r\n`.)
