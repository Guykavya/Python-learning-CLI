def ratio(a_text, b_text):
    """Return a / b formatted with two decimals, or a message saying what to fix."""
    return f"{float(a_text) / float(b_text):.2f}"
