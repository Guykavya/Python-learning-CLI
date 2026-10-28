# Convert between CSV and JSON

CSV has only text. JSON has numbers, `null`, lists. A converter has to decide the types and handle empty cells.

Write two functions in `solution.py`.

**`csv_to_json(csv_path, json_path, types=None)`**

- Read the CSV with `csv.DictReader` (open with `newline=""` and `encoding="utf-8"`).
- `types` is a dict that maps a column name to a function, for example `{"age": int, "price": float}`. Convert
  the cells of those columns with the function. An **empty** cell in a converted column becomes `None` (`null`).
  Columns that are not in `types` stay as text.
- Write the list of records to `json_path` as JSON (use `indent=2`, `encoding="utf-8"`).
- Return the number of records.

**`json_to_csv(json_path, csv_path)`**

- Read a JSON list of flat dicts. The columns are all keys, in the order they are first seen.
- Write them with `csv.DictWriter` (open with `newline=""`). A key that is missing in a record, and a `None`
  value, both become an empty cell.
- Return the number of records.

**Example**

```text
name,age,city
Asha,31,"Pune, MH"
Bo,,Delhi
```

with `types={"age": int}` gives `[{"name": "Asha", "age": 31, "city": "Pune, MH"}, {"name": "Bo", "age": null, "city": "Delhi"}]`.
