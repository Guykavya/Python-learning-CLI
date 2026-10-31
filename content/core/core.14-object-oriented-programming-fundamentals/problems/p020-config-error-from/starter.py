class ConfigError(Exception):
    pass


def parse_port(text):
    # TODO: int(), wrap ValueError in ConfigError "from" it; check the range
    return int(text)


def load_port(settings):
    # TODO: wrap a missing key in ConfigError "from" the KeyError
    return parse_port(settings["port"])
