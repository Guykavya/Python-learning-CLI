## Hint 1

Why is `line.split(",")` a bad idea for CSV? Which class of the `csv` module gives you each row as a dict keyed by the header?

## Hint 2

```
total = 0.0
with open(path, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        cell = row[column]
        if cell.strip() != "": total += float(cell)
return total
```
