import shlex


def split_command(line: str) -> list[str]:
    """Split like a POSIX shell: quotes group words, an unquoted # starts a comment."""
    return line.split()


def join_command(args: list[str]) -> str:
    """Join arguments into one line that split_command turns back into the same list."""
    return " ".join(args)


def parse_settings(line: str) -> dict[str, str]:
    """'name="Kavya B" city=Delhi' -> {'name': 'Kavya B', 'city': 'Delhi'}."""
    result = {}
    for token in line.split():
        key, value = token.split("=")
        result[key] = value
    return result
