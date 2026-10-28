class ConfigError(Exception):
    pass


def parse_port(text):
    try:
        number = int(text.strip())
    except ValueError as e:
        raise ConfigError(f"port must be a number, got {text!r}") from e
    if not 1 <= number <= 65535:
        raise ConfigError(f"port out of range: {number}")
    return number


def load_port(settings):
    try:
        text = settings["port"]
    except KeyError as e:
        raise ConfigError("missing setting: port") from e
    return parse_port(text)
