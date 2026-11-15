# Trace: five pagination loops

Below, `get_page` is a tiny fake page-number API over a list called `ORDERS` (3 orders per
page, page 1 is the first page). Five loops try to read all the orders. Some of them are
wrong, and they are wrong in different ways: they ask for the wrong pages, ask for too many,
or lose orders.

Work out exactly what this program prints. Each `run` call prints the function name, the list
of page numbers that were requested, and the list of orders collected. The program needs no
input and no network.

```python
ORDERS = []
requested = []


def get_page(page, per_page=3):
    """A fake page-number API over the list ORDERS."""
    requested.append(page)
    start = (page - 1) * per_page
    chunk = ORDERS[start:start + per_page]
    more = start + per_page < len(ORDERS)
    return {"data": chunk, "page": page, "next_page": page + 1 if more else None}


def short_page_stops():
    got, page = [], 1
    while True:
        body = get_page(page)
        got += body["data"]
        if len(body["data"]) < 3:
            break
        page += 1
    return got


def count_pages_first():
    got = []
    for page in range(1, len(ORDERS) // 3 + 1):
        got += get_page(page)["data"]
    return got


def skips_first_page():
    got = []
    body = get_page(1)
    while body["next_page"] is not None:
        body = get_page(body["next_page"])
        got += body["data"]
    return got


def starts_at_zero():
    got, page = [], 0
    while True:
        data = get_page(page)["data"]
        if not data:
            break
        got += data
        page += 1
    return got


def follows_next_page():
    got, page = [], 1
    while page is not None:
        body = get_page(page)
        got += body["data"]
        page = body["next_page"]
    return got


def run(fn, orders):
    ORDERS[:] = orders
    requested.clear()
    got = fn()
    print(fn.__name__, requested, got)


seven = [101, 102, 103, 104, 105, 106, 107]
six = seven[:6]
run(short_page_stops, seven)
run(short_page_stops, six)
run(count_pages_first, seven)
run(count_pages_first, six)
run(skips_first_page, seven)
run(starts_at_zero, seven)
run(follows_next_page, six)
```

Write your answer in `answer.txt`, one line per printed line, exactly as `print` would write it.

**Example (a different call)**

With `ORDERS = [1, 2, 3, 4]`, `run(follows_next_page, [1, 2, 3, 4])` would print

```
follows_next_page [1, 2] [1, 2, 3, 4]
```

because page 1 is `[1, 2, 3]` with `next_page` 2, and page 2 is `[4]` with `next_page` None.
