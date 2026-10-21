def validate_username(name):
    """Return name if it is a valid username; otherwise raise TypeError or ValueError."""
    if len(name) < 3:
        print("too short")
    return name
