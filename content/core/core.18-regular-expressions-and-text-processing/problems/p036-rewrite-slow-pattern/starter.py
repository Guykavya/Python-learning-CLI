import re

# Replace this with a fast pattern that accepts exactly the same strings as
# re.compile(r"(\w+\s?)*") under fullmatch.
SAFE_RE = re.compile(r"$^")
