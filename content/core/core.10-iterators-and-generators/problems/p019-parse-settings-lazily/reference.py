def parse_settings(lines):
    for number, line in enumerate(lines, start=1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        if "=" not in text:
            raise ValueError(f"line {number}: missing '='")
        key, value = text.split("=", 1)
        yield key.strip(), value.strip()
