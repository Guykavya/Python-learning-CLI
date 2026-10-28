## Approach

`iter(callable, sentinel)` turns "call this until it gives the stop value" into an iterator. That
fits pagination exactly: the callable fetches the next page, and the empty list `[]` is the stop
value (`[] == []` is `True`, so an empty page ends the loop). The callable needs memory between
calls, the page number, so it is a closure with `nonlocal`. Retries live inside the callable, so the
iterator never sees a failure that was fixed by a retry.

`items` is a two-line generator. Because `yield from page` hands out one item at a time, the next
page is fetched only when the `for` loop needs it.

## Code

```python
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
```

## Complexity

O(total items + number of fetches) time. Memory: one page at a time.

## Another way

`pages` can be a generator instead:

```python
def pages(fetch_page, retries=2):
    n = 0
    while True:
        page = fetch_with_retries(fetch_page, n, retries)   # a helper with the retry loop
        if not page:
            return
        yield page
        n += 1
```

This version needs no `nonlocal`, and many people find it easier to read. The `iter(callable,
sentinel)` form is worth knowing because it turns any "call until done" API into an iterator in one line.
`items` could also be `itertools.chain.from_iterable(pages(fetch_page, retries))`.
