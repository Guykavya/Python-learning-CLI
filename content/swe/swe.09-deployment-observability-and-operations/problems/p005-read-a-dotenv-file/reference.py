import re

NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def parse_dotenv(text):
    values = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        name, sep, value = line.partition("=")
        name = name.strip()
        if not sep:
            raise ValueError(f"line {number}: expected NAME=value")
        if not NAME.fullmatch(name):
            raise ValueError(f"line {number}: {name!r} is not a valid variable name")
        value = value.strip()
        if value[:1] in ("'", '"'):
            quote = value[0]
            if len(value) < 2 or value[-1] != quote:
                raise ValueError(f"line {number}: unterminated {quote} quote")
            value = value[1:-1]
        values[name] = value
    return values
