async def paginate(fetch_page):
    """Yield every item of pages 1, 2, ... until an empty page, fetching lazily."""
    # TODO: this fetches EVERY page before yielding anything. A caller that
    # stops early still pays for all the pages.
    all_items = []
    page = 1
    while True:
        items = await fetch_page(page)
        if not items:
            break
        all_items.extend(items)
        page += 1
    for item in all_items:
        yield item
