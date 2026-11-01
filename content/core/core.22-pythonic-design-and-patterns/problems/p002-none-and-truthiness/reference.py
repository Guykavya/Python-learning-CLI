def describe(value):
    if value is None:
        return "missing"
    if value is True:
        return "yes"
    if value is False:
        return "no"
    if value == 0:
        return "zero"
    if value == "":
        return "empty text"
    if value == []:
        return "empty list"
    return f"value {value!r}"


def first_non_empty(values, default=None):
    for v in values:
        if v is not None:
            return v
    return default


def config_get(config, key, default):
    value = config.get(key)
    return default if value is None else value
