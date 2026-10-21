## Hint 1

Two different problems: a missing key and a bad value. Which one can you check with a simple
`if`, and which one needs `try` because only the converter knows the rules?

## Hint 2

Functions are objects with a `__name__` attribute: `int.__name__` is `'int'`. Inside
`except ValueError as e:`, `raise NewError(...) from e` records `e` as the cause.

## Hint 3

```
for field, converter in schema.items():
    if field not in record: raise ValueError(f"missing field {field!r}")
    value = record[field]
    try:
        result[field] = converter(value)
    except ValueError as e:
        raise ValueError(f"field ...") from e
```
