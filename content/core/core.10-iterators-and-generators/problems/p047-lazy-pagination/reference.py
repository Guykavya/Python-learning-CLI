from collections.abc import Callable, Iterator


def pages(fetch_page: Callable[[int], list], retries: int = 2) -> Iterator[list]:
    page_number = 0

    def next_page() -> list:
        nonlocal page_number
        attempts_left = retries
        while True:
            try:
                page = fetch_page(page_number)
            except ConnectionError:
                if attempts_left == 0:
                    raise
                attempts_left -= 1
            else:
                page_number += 1
                return page

    return iter(next_page, [])


def items(fetch_page: Callable[[int], list], retries: int = 2) -> Iterator[object]:
    for page in pages(fetch_page, retries):
        yield from page
