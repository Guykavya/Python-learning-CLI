def set_age(age: int) -> int:
    if isinstance(age, bool) or not isinstance(age, int):
        raise TypeError("age must be an int")
    if age < 0 or age > 150:
        raise ValueError("age must be between 0 and 150")
    return age


def require_str_list(values: object) -> list[str]:
    if not isinstance(values, list):
        raise TypeError("expected a list")
    result: list[str] = []
    for item in values:
        if not isinstance(item, str):
            raise TypeError("every item must be a str")
        result.append(item)
    return result
