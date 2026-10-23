## Hint 1

Write the four signatures first. `parse_rows` returns a **fixed pair** of two lists with different contents: which hint describes "a list of (str, int) pairs and a list of strings, together"? Which two functions can return "nothing" for no rows?

## Hint 2

For `parse_rows`, handle each line in this order: skip blank lines; split on `","`; check the number of parts; strip the name; convert the age in a `try`; check the range. Any failure appends the original line to the bad list and moves on. For `age_buckets`, start from a dict that already has the four keys.

## Hint 3

```
def parse_rows(lines):
    rows = []; bad = []
    for line in lines:
        if line.strip() == "": continue
        parts = line.split(",")
        if len(parts) != 2: bad.append(line); continue
        name = parts[0].strip()
        try: age = int(parts[1])
        except ValueError: bad.append(line); continue
        if name == "" or age < 0 or age > 150: bad.append(line); continue
        rows.append((name, age))
    return rows, bad

oldest: loop keeping the best row so far, starting from None
mean_age: None if no rows else sum of ages / len(rows)
```
