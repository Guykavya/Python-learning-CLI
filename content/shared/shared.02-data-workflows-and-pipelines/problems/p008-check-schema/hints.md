## Hint 1

For one schema field there are four cases, checked in this order: not in the record, `None`,
wrong type, fine. Which of them depend on `required`? Which Python test tells "missing" from
"present but None"? For the type, what does `isinstance(True, int)` return, and what extra
check do you need before `isinstance`?

## Hint 2

```
for field, rule in schema.items():
    if field not in record:  if required: add "missing";  continue
    value = record[field]
    if value is None:        if required: add "null";     continue
    if not type_ok(value, rule["type"]): add f"{field}: expected {T.__name__}, got {type(value).__name__}"
for field in record:
    if field not in schema: add "unexpected field"

type_ok: if value is a bool -> only ok when expected is bool
         if expected is float -> ok for int or float
         else isinstance(value, expected)
```
