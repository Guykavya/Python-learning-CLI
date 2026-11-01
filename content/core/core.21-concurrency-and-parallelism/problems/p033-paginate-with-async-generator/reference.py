async def paginate(fetch_page):
    """Yield every item of pages 1, 2, ... until an empty page, fetching lazily."""
    page = 1
    while True:
        items = await fetch_page(page)
        if not items:
            return
        for item in items:
            yield item
        page += 1
