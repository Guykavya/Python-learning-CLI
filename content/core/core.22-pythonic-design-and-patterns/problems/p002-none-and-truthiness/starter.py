def describe(value):
    if value == None:
        return "missing"
    if value == True:
        return "yes"
    if value == False:
        return "no"
    if not value:
        return "empty"
    return "value " + repr(value)


def first_non_empty(values, default=None):
    for v in values:
        if v:
            return v
    return default


def config_get(config, key, default):
    value = config.get(key)
    if not value:
        return default
    return value
