import re

LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)")


def md_links(text: str) -> str:
    return LINK.sub(r'<a href="\2">\1</a>', text)
