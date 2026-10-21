# Validate a whole sign-up form

A sign-up page must show the user **every** problem at once, next to the field it belongs to,
not one at a time. Write `validate_signup(form)` where `form` is a dict of field name to the text
the user typed. Return a dict from field name to an error message, with one entry for each field
that has a problem. Return `{}` when the form is valid. Fields in `form` that are not listed
below are ignored.

A good design (section 9 and core.06's dispatch tables): write one small validator per field
that **raises** `ValueError(message)` when the value is bad, keep them in a dict, and let
`validate_signup` call each one and catch `ValueError` to record the message.

| Field | Rule | Message |
|---|---|---|
| every field | missing, or empty after `strip()` | `this field is required` |
| `username` | 3 to 15 characters, each a letter, digit or `_` | `use 3 to 15 letters, digits or _` |
| `age` | `int()` works | `age must be a whole number, like 21` |
| `age` | from 13 to 120 | `age must be from 13 to 120` |
| `email` | exactly one `@`, text on both sides, a `.` in the part after `@` that is not its first or last character | `email must look like name@example.com` |
| `password` | at least 8 characters | `password must be at least 8 characters` |
| `password` | contains a digit | `password must contain a digit` |
| `password` | does not contain the username, ignoring case (only checked when the username itself is valid) | `password must not contain your username` |

Strip every value before checking it. For each field, report only the **first** rule it breaks,
in the order listed.

**Example**

```python
validate_signup({"username": "asha_99", "age": "21", "email": "asha@mail.in", "password": "tiger2024"})
# {}

validate_signup({"username": "as", "age": "twelve", "email": "asha.mail.in", "password": "tiger"})
# {'username': 'use 3 to 15 letters, digits or _',
#  'age': 'age must be a whole number, like 21',
#  'email': 'email must look like name@example.com',
#  'password': 'password must be at least 8 characters'}
```
