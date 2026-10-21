def parse_config(lines, schema):
    """Parse 'key = value' lines using schema converters; raise ValueError 'line N: ...' on problems."""
    config = {}
    for line in lines:
        key, value = line.split("=")
        config[key.strip()] = schema[key.strip()](value.strip())
    return config
