import re

PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_]\w*)\s*\}\}")


def render(template: str, values: dict) -> str:
    def fill(m: re.Match) -> str:
        name = m.group(1)
        if name in values:
            return str(values[name])
        return m.group(0)

    return PLACEHOLDER_RE.sub(fill, template)
