"""Pull email addresses out of free text (the club sign-up sheet).

Users report: two addresses on one line come back as one string, addresses with no dot
in the domain are accepted, capital letters break it, and more. Find the bugs and fix them.
"""
import re

EMAIL_RE = re.compile(r"[\w.+-]+@.+.[a-z]+")


def extract_emails(text: str) -> list[str]:
    """Every email address in `text`, in order, spelled as written."""
    return EMAIL_RE.findall(text)
