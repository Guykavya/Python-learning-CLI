from collections.abc import Iterator


def flatten(data: list | tuple) -> Iterator[object]:
    for item in data:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item


def walk(tree: dict, prefix: str = "") -> Iterator[tuple[str, object]]:
    for name, value in tree.items():
        path = prefix + name
        if isinstance(value, dict):
            yield from walk(value, path + "/")
        else:
            yield path, value
