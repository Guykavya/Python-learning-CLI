# Report every problem at once with an ExceptionGroup

A sign-up form with three mistakes should not say "fix the name", then after the fix "fix the
email", then "fix the age". It should report all three at once. Normal `raise` can only raise one
exception. An **`ExceptionGroup`** wraps a list of exceptions into one, and the caller can handle each
kind with `except*`.

Write `validate_user(data)` in `solution.py`. `data` is a dict. Check the fields in this order:
`"name"`, `"email"`, `"age"`. For each field, add **at most one** error to a list:

| Field | Problem | Error to add |
|---|---|---|
| any of the three | key missing | `KeyError(<field name>)`, for example `KeyError("email")` |
| `name` | empty or only spaces | `ValueError("name must not be empty")` |
| `email` | no `@` in it | `ValueError("email must contain @")` |
| `age` | not an `int` | `TypeError("age must be an int")` |
| `age` | an `int` outside 0 to 150 | `ValueError("age must be between 0 and 150")` |

At the end: if the list has errors, `raise ExceptionGroup("invalid user", errors)`. If there are no
errors, return `None`. Extra keys in `data` are ignored. You may assume `name` and `email`, when
present, are strings.

**Example**

```python
validate_user({"name": "Kavya", "email": "k@x.in", "age": 19})   # returns None

try:
    validate_user({"name": " ", "age": "19"})
except ExceptionGroup as eg:
    print(eg.message)                         # invalid user
    for e in eg.exceptions:
        print(type(e).__name__, e)
# ValueError name must not be empty
# KeyError 'email'
# TypeError age must be an int
```

(A `KeyError` prints its key with quotes: `print(KeyError("email"))` shows `'email'`.)
