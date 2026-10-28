import shlex


def split_command(line: str) -> list[str]:
    return shlex.split(line, comments=True)


def join_command(args: list[str]) -> str:
    return shlex.join(args)


def parse_settings(line: str) -> dict[str, str]:
    settings = {}
    for token in shlex.split(line, comments=True):
        key, sep, value = token.partition("=")
        if not sep or not key:
            raise ValueError(f"expected key=value, got {token!r}")
        settings[key] = value
    return settings
