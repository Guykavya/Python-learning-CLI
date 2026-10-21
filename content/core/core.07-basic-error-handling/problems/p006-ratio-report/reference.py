def ratio(a_text, b_text):
    """Return a / b formatted with two decimals, or a message saying what to fix."""
    try:
        result = float(a_text) / float(b_text)
    except ValueError:
        return "Both values must be numbers, like 3 or 2.5."
    except ZeroDivisionError:
        return "The second value must not be zero."
    return f"{result:.2f}"
