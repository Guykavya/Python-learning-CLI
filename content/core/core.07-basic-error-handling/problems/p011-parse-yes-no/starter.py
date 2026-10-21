def parse_yes_no(text):
    """Return True or False for a yes/no answer; raise ValueError if it is neither."""
    return text.strip().lower() == "yes"
