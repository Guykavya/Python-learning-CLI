import re

REF = re.compile(r"[A-Z]+-[0-9]{2}-[0-9]{2}-[0-9]{2}")


def is_valid_ref(s):
    """True when the whole text is a reference like AB-12-34-56."""
    return REF.fullmatch(s) is not None
