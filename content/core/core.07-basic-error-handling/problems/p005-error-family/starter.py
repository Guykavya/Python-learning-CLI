def error_family(func, *args):
    """Call func(*args) and return 'ok', 'lookup', 'arithmetic', 'value' or 'type'."""
    func(*args)
    return "ok"
