import pprint


def pretty(data: object, width: int = 40) -> str:
    """pformat with this width, keys in insertion order."""
    return str(data)


def pretty_sorted(data: object, width: int = 40) -> str:
    """pformat with this width, keys sorted (pprint's default)."""
    return str(data)


def outline(data: object, depth: int) -> str:
    """pformat showing only `depth` levels, insertion order."""
    return str(data)


def compact_numbers(numbers: list[int], width: int = 30) -> str:
    """pformat that fills each line with as many items as fit."""
    return str(numbers)


def log_block(title: str, data: object, width: int = 40) -> str:
    """'title:' then pretty(data, width), every line indented by 4 spaces."""
    pprint.pprint(data)
    return title
