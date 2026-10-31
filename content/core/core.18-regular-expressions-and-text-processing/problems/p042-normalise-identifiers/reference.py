import re

ID_RE = re.compile(r"([A-Za-z]{2,4}) *[-_/]? *(\d{1,6})")


def normalise_ids(lines: list[str]) -> list[str]:
    result = []
    seen = set()
    for line in lines:
        m = ID_RE.fullmatch(line.strip())
        if m is None:
            continue
        prefix, number = m.groups()
        normal = f"{prefix.upper()}-{number.zfill(4)}"
        if normal not in seen:
            seen.add(normal)
            result.append(normal)
    return result
