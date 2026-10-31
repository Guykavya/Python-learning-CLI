import re

# Each word is followed by exactly one whitespace character, except possibly the last word.
# A run of letters can now be matched in only one way, so a failure is found quickly.
SAFE_RE = re.compile(r"(?:\w+\s)*\w*")
