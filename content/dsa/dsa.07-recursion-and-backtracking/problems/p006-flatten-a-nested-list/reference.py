def flatten(xs):
    result = []
    for item in xs:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
