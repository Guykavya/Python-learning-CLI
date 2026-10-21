def error_family(func, *args):
    """Call func(*args) and return 'ok', 'lookup', 'arithmetic', 'value' or 'type'."""
    try:
        func(*args)
    except LookupError:
        return "lookup"
    except ArithmeticError:
        return "arithmetic"
    except ValueError:
        return "value"
    except TypeError:
        return "type"
    return "ok"
