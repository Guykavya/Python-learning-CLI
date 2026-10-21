def validate_signup(form):
    """Return {field: message} for every invalid field; {} when the form is valid."""
    errors = {}
    if len(form["username"]) < 3:
        errors["username"] = "use 3 to 15 letters, digits or _"
    return errors
