## Hint 1

`csv.DictReader` gives you one dict per row, with strings as values. Where would you apply `types[column]`, and what
must you check before calling it on a cell like `""`? For the way back: which `DictWriter` argument handles a key
that is missing in a record?

## Hint 2

```
csv_to_json:
  records = []
  for row in DictReader(f):
      for col, func in types.items():
          if col in row: row[col] = None if row[col] == "" else func(row[col])
      records.append(row)
  json.dump(records, out, indent=2)
json_to_csv:
  fields = all keys in first-seen order
  DictWriter(f, fieldnames=fields, restval="")
  writerow({k: "" if v is None else v for k, v in rec.items()})
```
