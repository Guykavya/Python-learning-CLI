def validate_user(data):
    errors = []

    if "name" not in data:
        errors.append(KeyError("name"))
    elif data["name"].strip() == "":
        errors.append(ValueError("name must not be empty"))

    if "email" not in data:
        errors.append(KeyError("email"))
    elif "@" not in data["email"]:
        errors.append(ValueError("email must contain @"))

    if "age" not in data:
        errors.append(KeyError("age"))
    elif not isinstance(data["age"], int):
        errors.append(TypeError("age must be an int"))
    elif not 0 <= data["age"] <= 150:
        errors.append(ValueError("age must be between 0 and 150"))

    if errors:
        raise ExceptionGroup("invalid user", errors)
    return None
