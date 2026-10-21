def describe_error(err):
    """Return a one-line description of the exception object err."""
    name = type(err).__name__
    if not err.args:
        return name
    if isinstance(err, KeyError):
        return f"{name}: missing key {err.args[0]}"
    return name + ": " + ", ".join(str(arg) for arg in err.args)
