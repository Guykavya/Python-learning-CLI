## Approach

Two layers. **Validators** know the rules for one field; they raise `ValueError` with a message
for the user, exactly like built-in functions raise for bad values. **The collector** knows that
the form needs every message: it calls each validator inside its own `try`, so one failure never
stops the others, and turns each exception into a dict entry. The age validator translates
`int()`'s technical error into a friendly message `from None`. The password validator re-uses the
username validator (catching its `ValueError`) to decide whether the cross-field rule applies.

## Code

```python
FIELDS = ["username", "age", "email", "password"]


def check_username(value, form):
    if not 3 <= len(value) <= 15 or not all(ch.isalnum() or ch == "_" for ch in value):
        raise ValueError("use 3 to 15 letters, digits or _")


def check_age(value, form):
    try:
        age = int(value)
    except ValueError:
        raise ValueError("age must be a whole number, like 21") from None
    if not 13 <= age <= 120:
        raise ValueError("age must be from 13 to 120")


def check_email(value, form):
    local, at, domain = value.partition("@")
    ok = (at and local and "@" not in domain and "." in domain[1:-1])
    if not ok:
        raise ValueError("email must look like name@example.com")


def check_password(value, form):
    if len(value) < 8:
        raise ValueError("password must be at least 8 characters")
    if not any(ch.isdigit() for ch in value):
        raise ValueError("password must contain a digit")
    username = form.get("username", "").strip()
    try:
        check_username(username, form)
    except ValueError:
        return
    if username.lower() in value.lower():
        raise ValueError("password must not contain your username")


VALIDATORS = {
    "username": check_username,
    "age": check_age,
    "email": check_email,
    "password": check_password,
}


def validate_signup(form):
    """Return {field: message} for every invalid field; {} when the form is valid."""
    errors = {}
    for field in FIELDS:
        value = form.get(field, "").strip()
        if not value:
            errors[field] = "this field is required"
            continue
        try:
            VALIDATORS[field](value, form)
        except ValueError as e:
            errors[field] = str(e)
    return errors
```

## Complexity

O(total length of the form's values).

## Another way

Validators could **return** an error string or `None` instead of raising. That works, but every
caller must remember to check the result; with exceptions, a validator used elsewhere (say, when
an admin edits a user) cannot be ignored by accident. The raising style also lets a validator
call other code that raises, such as `int()`, and let its own message through or translate it.
