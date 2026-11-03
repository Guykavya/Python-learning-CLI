# A schema check that lists every problem

A **schema** (or data contract) says which fields a record must have and what type each one
is. Checking it at the door, before any transform, turns a confusing `KeyError` deep inside
your code into a clear message like `amount: expected str, got float`.

Write

```python
def check_schema(record, schema):
```

`schema` maps a field name to its rule:

```python
ORDER_SCHEMA = {
    "id":       {"type": int,   "required": True},
    "status":   {"type": str,   "required": True},
    "amount":   {"type": str,   "required": True},
    "city":     {"type": str,   "required": False},
    "discount": {"type": float, "required": False},
}
```

Return a **list of error strings** (an empty list means the record is valid). Check the fields
in schema order and add at most one error per field:

| situation | error string |
|---|---|
| a required field is not in the record | `"id: missing"` |
| a required field is `None` | `"id: null"` |
| the value has the wrong type | `"id: expected int, got str"` (use the types' `__name__`) |

Then, after all schema fields, add `"<name>: unexpected field"` for every key of the record
that is **not** in the schema, in the record's order.

More rules:

- An **optional** field (`"required": False`) may be missing or `None`. If it has any other
  value, the type is still checked.
- `bool` is **not** an `int` here, even though `isinstance(True, int)` is `True` in Python
  (because `bool` is a subclass of `int`). `{"id": True}` gives `"id: expected int, got bool"`.
  A `bool` is only accepted where the schema says `bool`.
- A `float` field also accepts an `int` (JSON often writes `5.0` as `5`), but not a `bool`.
- Do not change the record.

**Example**

```python
check_schema({"id": 101, "status": "shipped", "amount": "19.99"}, ORDER_SCHEMA)
# []

check_schema({"id": "101", "status": None, "amount": 19.99, "city": None, "coupon": "X"}, ORDER_SCHEMA)
# ['id: expected int, got str', 'status: null', 'amount: expected str, got float', 'coupon: unexpected field']
```
