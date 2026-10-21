def run_pipeline(value, *steps, collect=False):
    """Pass value through each step left to right; return the result, or every value if collect."""
    history = [value]
    for step in steps:
        value = step(value)
        history.append(value)
    if collect:
        return history
    return value
