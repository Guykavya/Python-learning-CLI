## Approach

Strip the two text fields, leave passwords alone, check each field on its own.

```python
import re

USERNAME = re.compile(r"[a-z0-9_]{3,20}")
EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def validate_signup(form):
    clean = {
        "username": str(form.get("username", "")).strip(),
        "email": str(form.get("email", "")).strip(),
    }
    password = form.get("password", "")
    confirm = form.get("confirm", "")
    errors = {}
    if not USERNAME.fullmatch(clean["username"]):
        errors["username"] = "Use 3 to 20 characters: lower-case letters, digits and _"
    if not EMAIL.fullmatch(clean["email"]):
        errors["email"] = "Enter a valid email address"
    if len(password) < 10:
        errors["password"] = "Use at least 10 characters"
    if confirm != password:
        errors["confirm"] = "The passwords do not match"
    return clean, errors
```

Example: `{"username": "A", "email": "nope", "password": "short", "confirm": "different"}` fails all four checks, so the page can mark every field at once.

The function takes plain data and returns plain data, so the same rules can be tested with a dict (as here), called from a view with `request.form`, or reused in an API.

## Complexity

`O(total length of the fields)`.

## Another way

Return the first error only, or a list of messages per field (for the macro of problem 14). A regex for the email is a **shape** check; the only true proof of an address is sending a message to it.

## Not covered

Checking that the username is not already taken needs the database (problem 27).
