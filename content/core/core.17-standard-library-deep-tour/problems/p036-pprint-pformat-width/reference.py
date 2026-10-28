import pprint


def pretty(data: object, width: int = 40) -> str:
    return pprint.pformat(data, width=width, sort_dicts=False)


def pretty_sorted(data: object, width: int = 40) -> str:
    return pprint.pformat(data, width=width)


def outline(data: object, depth: int) -> str:
    return pprint.pformat(data, depth=depth, sort_dicts=False)


def compact_numbers(numbers: list[int], width: int = 30) -> str:
    return pprint.pformat(numbers, width=width, compact=True)


def log_block(title: str, data: object, width: int = 40) -> str:
    lines = [title + ":"]
    for line in pretty(data, width).splitlines():
        lines.append("    " + line)
    return "\n".join(lines)
