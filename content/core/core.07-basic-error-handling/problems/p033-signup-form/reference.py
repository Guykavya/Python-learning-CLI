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
