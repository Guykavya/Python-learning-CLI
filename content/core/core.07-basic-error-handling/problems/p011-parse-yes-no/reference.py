YES = ("yes", "y", "true", "1")
NO = ("no", "n", "false", "0")


def parse_yes_no(text):
    """Return True or False for a yes/no answer; raise ValueError if it is neither."""
    if not isinstance(text, str):
        raise TypeError(f"answer must be text (str), got {type(text).__name__}")
    word = text.strip().lower()
    if word in YES:
        return True
    if word in NO:
        return False
    raise ValueError(f"answer must be yes or no (also y/n, true/false, 1/0), got {text!r}")
