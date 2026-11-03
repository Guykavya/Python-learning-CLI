## Approach

A schema check must not stop at the first problem: whoever reads the quarantine file wants to
see *everything* that is wrong with a record. So we walk the schema, collect errors in a
list, and return the list.

For each field the cases are checked in a fixed order, and each one ends the work for that
field (`continue`), which is what guarantees at most one error per field:

1. `field not in record`: missing. Only an error if required.
2. `value is None`: null. Only an error if required. It must come before the type check,
   or a null would show up as `expected str, got NoneType`.
3. wrong type: an error whether required or not.

`is None` (not `if not value`) matters, because `0`, `""` and `False` are real values.

The `bool` rule exists because `bool` is a subclass of `int` in Python, so `isinstance(True, int)`
is `True`. In data, a `true` where a number belongs is a bug in the source; letting it through
would store order id `1`. So `type_ok` looks at bools first. The float rule (`int` accepted)
follows JSON, which has only one number type: `5.0` is often written `5`.

Extra fields are reported last. They are often harmless (the API added a field), but you want
to know about them: either the schema needs updating or the source sent something unexpected.

## Code

```python
def type_ok(value, expected):
    if isinstance(value, bool):
        return expected is bool
    if expected is float:
        return isinstance(value, (int, float))
    return isinstance(value, expected)


def check_schema(record, schema):
    errors = []
    for field, rule in schema.items():
        if field not in record:
            if rule["required"]:
                errors.append(f"{field}: missing")
            continue
        value = record[field]
        if value is None:
            if rule["required"]:
                errors.append(f"{field}: null")
            continue
        if not type_ok(value, rule["type"]):
            errors.append(f"{field}: expected {rule['type'].__name__}, got {type(value).__name__}")
    for field in record:
        if field not in schema:
            errors.append(f"{field}: unexpected field")
    return errors
```

## Complexity

O(s + r) for `s` schema fields and `r` record keys (dict lookups are O(1)).

## Another way

Libraries such as `jsonschema` or `pydantic` do the same job with a declarative schema and
nested objects. They are worth it in a big project; the hand-written version shows exactly
what they do. A stricter variant uses `type(value) is expected` (exact type), which rejects
bools for free, but also rejects subclasses you might want to allow.
