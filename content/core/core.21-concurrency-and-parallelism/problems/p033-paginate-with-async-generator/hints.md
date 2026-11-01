## Hint 1

An `async def` function that contains `yield` is an async generator: `async for` pulls one
item at a time, and the function pauses at each `yield` until the next item is wanted. So if
you fetch a page, `yield` its items one by one, and only then fetch the next page, when does
the next fetch happen? What happens to a paused generator when the caller `break`s?

## Hint 2

```
page = 1
loop forever:
    items = await fetch_page(page)
    if no items: return          # ends the async for
    for item in items:
        yield item               # pauses here until the caller wants more
    page += 1
```

Do not collect everything into a list first: that fetches all pages before the caller sees
the first item.
