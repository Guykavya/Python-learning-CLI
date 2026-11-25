## Hint 1

What happens to the file if you call `df.to_excel(path)` twice with the same path? Which object lets several `to_excel` calls share **one** open workbook? How do you leave the row labels out?

## Hint 2

```text
with pd.ExcelWriter(path) as writer:
    for name, frame in sheets.items():
        frame.to_excel(writer, sheet_name=name, index=False)
```
