def validate_signup(form):
    clean = {"username": form.get("username", ""), "email": form.get("email", "")}   # TODO: strip
    errors = {}
    # TODO: check username, email, password, confirm
    return clean, errors
