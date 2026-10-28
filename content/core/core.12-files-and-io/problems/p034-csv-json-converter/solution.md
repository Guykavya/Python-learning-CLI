## Approach

Reading: `DictReader` turns each row into a dict of strings. Apply the converter only to the columns named in
`types`, and map the empty string to `None`. Writing JSON: `json.dump` with `indent=2`.
Back: collect the field names with a loop that keeps the first-seen order (a list and `not in`, or a dict as an
ordered set), then use `DictWriter` with `restval=""` for missing keys and replace `None` with `""`.
Both CSV files are opened with `newline=""`, as the `csv` module needs.

## Code

```python
import csv
import json


def csv_to_json(csv_path, json_path, types=None):
    types = types or {}
    records = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for column, func in types.items():
                if column in row:
                    row[column] = None if row[column] == "" else func(row[column])
            records.append(row)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    return len(records)


def json_to_csv(json_path, csv_path):
    with open(json_path, encoding="utf-8") as f:
        records = json.load(f)
    fields = []
    for record in records:
        for key in record:
            if key not in fields:
                fields.append(key)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, restval="")
        writer.writeheader()
        for record in records:
            writer.writerow({k: ("" if v is None else v) for k, v in record.items()})
    return len(records)
```

## Complexity

Time O(rows x columns). Memory O(whole file), because both functions build the full list. For huge files, write
JSON Lines (one record per line) instead.

## Another way

Let the caller pass a converter for every column, with a default of `str`. Or guess the types: try `int`, then
`float`, else keep the text.
