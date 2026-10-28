# Dump JSON with sets and dates

`json.dumps` cannot write a `set`, a `date` or a `Path`. It raises `TypeError`.
You can fix this with the `default=` argument: a function that JSON calls for every object it does not know.

Write `dump_json(data)` in `solution.py`. It returns a JSON string (no file) with `sort_keys=True`, and:

- a `set` becomes a **sorted list**;
- a `date` or `datetime` becomes its ISO text (`isoformat()`);
- a `Path` becomes `str(path)`;
- any other unknown object still raises `TypeError`.

**Example**

```python
from datetime import date
dump_json({"tags": {"b", "a"}, "when": date(2024, 1, 5)})
# '{"tags": ["a", "b"], "when": "2024-01-05"}'
```
