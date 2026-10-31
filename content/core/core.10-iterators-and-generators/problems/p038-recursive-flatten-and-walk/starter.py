from collections.abc import Iterator


def flatten(data: list | tuple) -> Iterator[object]:
    yield from ()


def walk(tree: dict, prefix: str = "") -> Iterator[tuple[str, object]]:
    yield from ()
