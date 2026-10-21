## Approach

Loop over the schema, not the record, so extra fields are ignored and the order is the schema's.
A missing field is a simple, exact check. A bad value can only be detected by the converter, so
its call is the whole `try` block. The handler translates the converter's message (which does not
know the field name) into one that does, and `from e` keeps the original for debugging: the
traceback shows both, joined by "The above exception was the direct cause...".

## Code

```python
def convert_record(record, schema):
    """Return a new dict with each schema field converted; raise ValueError naming the field."""
    result = {}
    for field, converter in schema.items():
        if field not in record:
            raise ValueError(f"missing field {field!r}")
        value = record[field]
        try:
            result[field] = converter(value)
        except ValueError as e:
            raise ValueError(f"field {field!r}: could not convert {value!r} with {converter.__name__}") from e
    return result
```

## Complexity

O(number of schema fields), plus the converters' own cost.

## Another way

Handle the missing field EAFP-style too: `try: value = record[field] except KeyError: raise
ValueError(f"missing field {field!r}") from None`. Both are fine; the `in` check is simple and
exact here.
