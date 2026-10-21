def validate_username(name):
    """Return name if it is a valid username; otherwise raise TypeError or ValueError."""
    if not isinstance(name, str):
        raise TypeError(f"username must be text (str), got {type(name).__name__}")
    if not 3 <= len(name) <= 15:
        raise ValueError(f"username must be 3 to 15 characters long, got {len(name)}")
    for ch in name:
        if not (ch.isalnum() or ch == "_"):
            raise ValueError(f"username may only use letters, digits and _, found {ch!r}")
    if name[0].isdigit():
        raise ValueError("username must not start with a digit")
    return name
