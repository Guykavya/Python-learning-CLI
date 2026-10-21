def reverse(text):
    """Return text reversed, recursively."""
    if len(text) <= 1:
        return text
    return reverse(text[1:]) + text[0]


def _check(s):
    if len(s) <= 1:
        return True
    if s[0] != s[-1]:
        return False
    return _check(s[1:-1])


def is_palindrome(text):
    """Return True if text is a palindrome ignoring case and non-alphanumerics (recursively)."""
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    return _check(cleaned)
