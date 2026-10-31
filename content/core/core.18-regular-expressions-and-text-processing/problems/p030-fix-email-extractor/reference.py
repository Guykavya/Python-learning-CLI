import re

EMAIL_RE = re.compile(r"[\w.%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}\b")


def extract_emails(text: str) -> list[str]:
    """Every email address in `text`, in order, spelled as written."""
    return EMAIL_RE.findall(text)
