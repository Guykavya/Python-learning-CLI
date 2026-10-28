from collections.abc import Callable, Iterator


def pages(fetch_page: Callable[[int], list], retries: int = 2) -> Iterator[list]:
    return iter([])


def items(fetch_page: Callable[[int], list], retries: int = 2) -> Iterator[object]:
    yield from ()
