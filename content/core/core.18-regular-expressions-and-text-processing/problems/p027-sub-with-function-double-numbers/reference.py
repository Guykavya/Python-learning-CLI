import re

INT_RE = re.compile(r"(?<![\w.])\d+(?!\w|\.\d)")


def _double(m: re.Match) -> str:
    return str(int(m.group()) * 2)


def double_numbers(s: str) -> str:
    return INT_RE.sub(_double, s)
