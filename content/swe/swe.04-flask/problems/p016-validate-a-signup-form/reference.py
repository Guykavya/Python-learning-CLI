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
