import re

KV_RE = re.compile(r"\s*(?P<key>[A-Za-z_]\w*)\s*=\s*(?P<value>.*?)\s*")


def parse_kv(line: str) -> dict[str, str] | None:
    m = KV_RE.fullmatch(line)
    if m is None:
        return None
    return m.groupdict()
