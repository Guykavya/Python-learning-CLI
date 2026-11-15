## Hint 1

Think of one day as one box that is either completely old or completely new, never a mix. Two
things can go wrong while you refill a box: the network fails while you are *reading* the day,
or the database rejects a row while you are *writing* it. For each one, where must the
`DELETE` be so that the old contents survive? Which Python construct makes "delete + all
inserts" succeed or fail together?

Then the two data surprises: what happens with a plain `INSERT` when order 5 arrives twice, or
when order 7 is already stored under another day?

## Hint 2

```
if start > end: raise ValueError
CREATE TABLE IF NOT EXISTS ...
day = start
while day <= end:
    key = day.isoformat()
    by_id = {}                                  # pages may repeat an order
    page = 1
    while page is not None:
        body = GET /v1/orders?created_on=key&page=page   (raise_for_status)
        for o in body["data"]: by_id[o["id"]] = o
        page = body["next_page"]
    with conn:
        DELETE FROM orders WHERE order_date = key
        INSERT ... ON CONFLICT (id) DO UPDATE SET order_date = excluded.order_date, ...
    counts[key] = len(by_id)
    day += timedelta(days=1)
return counts
```
