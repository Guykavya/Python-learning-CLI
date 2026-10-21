def parse_config(lines, schema):
    """Parse 'key = value' lines using schema converters; raise ValueError 'line N: ...' on problems."""
    config = {}
    first_seen = {}
    for n, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            raise ValueError(f"line {n}: expected 'key = value', got {line!r}")
        key, value = key.strip(), value.strip()
        if key not in schema:
            raise ValueError(f"line {n}: unknown setting {key!r}; known settings: {', '.join(sorted(schema))}")
        if key in first_seen:
            raise ValueError(f"line {n}: {key!r} is set twice (first on line {first_seen[key]})")
        first_seen[key] = n
        try:
            config[key] = schema[key](value)
        except ValueError as e:
            raise ValueError(f"line {n}: bad value for {key!r}: {value!r}") from e
    missing = sorted(set(schema) - set(config))
    if missing:
        raise ValueError(f"missing settings: {', '.join(missing)}")
    return config
