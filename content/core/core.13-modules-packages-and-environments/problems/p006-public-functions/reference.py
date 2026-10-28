def public_functions(module):
    result = []
    for name in dir(module):
        if name.startswith("_"):
            continue
        value = getattr(module, name)
        if callable(value) and getattr(value, "__module__", None) == module.__name__:
            result.append(name)
    return sorted(result)
