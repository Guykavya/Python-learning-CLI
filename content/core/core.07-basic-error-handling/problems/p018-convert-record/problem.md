# Convert a record, keeping the cause

Rows read from a form or a CSV file arrive as dicts of **strings**. Write
`convert_record(record, schema)` that returns a **new** dict with each field converted.

`schema` maps each field name to a converter function such as `int`, `float` or `str`. Go through
the fields **in schema order**:

- If the field is missing from `record`: raise `ValueError(f"missing field {field!r}")`.
- Call `converter(record[field])`. If it raises `ValueError`, raise a **new** `ValueError` that
  names the field, the bad value and the converter, and chain the original with `from e`
  (section 11):
  `field <field!r>: could not convert <value!r> with <converter name>`.
  The converter's name is `converter.__name__` (`'int'`, `'float'`, ...).
- Fields in `record` that are not in `schema` are left out of the result.
- `record` itself must not change.

**Example**

```python
schema = {"name": str, "age": int, "height": float}
convert_record({"name": "Asha", "age": "21", "height": "1.62", "city": "Pune"}, schema)
# {'name': 'Asha', 'age': 21, 'height': 1.62}

convert_record({"name": "Ravi", "age": "twenty", "height": "1.7"}, schema)
# ValueError: field 'age': could not convert 'twenty' with int
#   (its __cause__ is the original ValueError from int('twenty'))

convert_record({"name": "Meena", "height": "1.5"}, schema)
# ValueError: missing field 'age'
```
