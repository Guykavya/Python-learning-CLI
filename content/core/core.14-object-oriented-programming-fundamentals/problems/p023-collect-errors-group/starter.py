def validate_user(data):
    # TODO: collect every problem in a list, then raise ExceptionGroup("invalid user", errors)
    if "name" not in data:
        raise KeyError("name")
    return None
