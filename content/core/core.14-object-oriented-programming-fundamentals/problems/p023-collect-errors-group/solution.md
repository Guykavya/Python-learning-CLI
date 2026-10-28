## Approach

An exception is an object; you can create one without raising it (chapter section 19). So the
function walks through the fields, **collects** an exception object for each problem in a list, and
only at the end raises them together as one `ExceptionGroup`.

For each field, the first question is "is it there?". Only if it is, the value is checked. `if/elif`
makes sure one field adds at most one error, and for `age` the type check comes before the range check
(comparing `"19" <= 150` would itself raise a `TypeError`).

`ExceptionGroup` refuses an empty list, so raise it only when there are errors. Even a single problem
is raised inside a group: callers can always handle the result the same way, with `except*`.

## Code

```python
def validate_user(data):
    errors = []

    if "name" not in data:
        errors.append(KeyError("name"))
    elif data["name"].strip() == "":
        errors.append(ValueError("name must not be empty"))

    if "email" not in data:
        errors.append(KeyError("email"))
    elif "@" not in data["email"]:
        errors.append(ValueError("email must contain @"))

    if "age" not in data:
        errors.append(KeyError("age"))
    elif not isinstance(data["age"], int):
        errors.append(TypeError("age must be an int"))
    elif not 0 <= data["age"] <= 150:
        errors.append(ValueError("age must be between 0 and 150"))

    if errors:
        raise ExceptionGroup("invalid user", errors)
    return None
```

## Complexity

O(1): three fields, a few checks each (plus O(k) for `strip` and `in` on strings of length k).

## Another way

The caller handles each kind separately:

```python
try:
    validate_user(form)
except* KeyError as group:
    print("missing:", [e.args[0] for e in group.exceptions])
except* ValueError as group:
    print("bad values:", [str(e) for e in group.exceptions])
```

Both `except*` clauses can run for the same group. In a bigger program you would use your own
`FieldError(field, message)` class instead of built-in errors, so the group carries the field name too.
