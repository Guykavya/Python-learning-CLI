## Hint 1

If `validate_signup` raised at the first bad field, the user would see one problem at a time.
Where must the `try` be so that every field is checked?

## Hint 2

Write `check_age(value, form)` and friends: each returns nothing when the value is good and
raises `ValueError("...")` when it is not. A dict `{"age": check_age, ...}` lets one loop call
them all. Why pass `form` too? (Look at the last password rule.)

## Hint 3

```
for field in FIELDS:
    value = form.get(field, "").strip()
    if not value: errors[field] = "this field is required"; continue
    try: VALIDATORS[field](value, form)
    except ValueError as e: errors[field] = str(e)
```
For the password rule, re-use `check_username` to decide whether the username is valid.
