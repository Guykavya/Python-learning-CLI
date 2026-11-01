import asyncio
import inspect

from solution import paginate


def make_fetch(pages):
    """pages: list of lists; page n is pages[n-1]; past the end, pages are empty."""
    calls = []

    async def fetch_page(n):
        calls.append(n)
        await asyncio.sleep(0)
        return list(pages[n - 1]) if n <= len(pages) else []

    return fetch_page, calls


async def collect(agen, limit=None):
    out = []
    async for item in agen:
        out.append(item)
        if limit is not None and len(out) == limit:
            break
    return out


def test_is_an_async_generator():
    fetch, calls = make_fetch([[1]])
    gen = paginate(fetch)
    assert inspect.isasyncgen(gen), (
        "paginate(...) must return an async generator: write 'async def paginate' with "
        "'yield' inside, and no 'return <list>'."
    )
    assert calls == [], f"Just creating the generator fetched pages {calls}; nothing should run yet."
    asyncio.run(gen.aclose())


def test_all_items_in_order():
    fetch, calls = make_fetch([["a", "b"], ["c"], ["d", "e"]])
    items = asyncio.run(collect(paginate(fetch)))
    assert items == ["a", "b", "c", "d", "e"], f"Got {items}. Yield page 1's items, then page 2's, ..."
    assert calls == [1, 2, 3, 4], (
        f"Pages fetched: {calls}. Stop at the first empty page (page 4 here) and fetch each page once."
    )


def test_stops_early_without_fetching_more():
    fetch, calls = make_fetch([[1, 2], [3, 4], [5, 6], [7], [8]])
    items = asyncio.run(collect(paginate(fetch), limit=4))
    assert items == [1, 2, 3, 4]
    assert calls == [1, 2], (
        f"The caller stopped after page 2's last item, but pages {calls} were fetched. Fetch the "
        "next page only when the next item is asked for: yield items as you go, do not build a "
        "list of everything first."
    )


def test_first_item_arrives_after_one_fetch():
    fetch, calls = make_fetch([[1], [2], [3]])

    async def main():
        gen = paginate(fetch)
        first = await anext(gen)
        seen = list(calls)
        await gen.aclose()
        return first, seen

    first, seen = asyncio.run(main())
    assert first == 1 and seen == [1], (
        f"To produce the first item, pages {seen} were fetched. Only page 1 is needed."
    )


def test_empty_first_page():
    fetch, calls = make_fetch([])
    assert asyncio.run(collect(paginate(fetch))) == [], "An empty page 1 means no items at all."
    assert calls == [1], f"Pages fetched: {calls}; only page 1 should be fetched."


def test_pages_of_different_sizes():
    fetch, _ = make_fetch([[1, 2, 3, 4, 5], [6], [7, 8]])
    assert asyncio.run(collect(paginate(fetch))) == [1, 2, 3, 4, 5, 6, 7, 8], (
        "Do not assume pages have the same size; stop only on an EMPTY page."
    )
