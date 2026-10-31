import re

NAME_RE = re.compile(r"^([\w'-]+),[ \t]*([\w'-]+(?: [\w'-]+)*)[ \t]*$", re.MULTILINE)


def swap_names(text: str) -> str:
    return NAME_RE.sub(r"\2 \1", text)
