## Hint 1

The loop needs one variable: the page you are about to request. What is its value before the
first request? After each answer, where does its next value come from? Which value of it
means "stop"? If you write the loop condition in terms of that variable, the "first request"
needs no special case.

## Hint 2

```
orders = []
page = 1
while page is not None:
    response = client.get("/v1/orders", params={"page": page, "per_page": per_page})
    response.raise_for_status()
    body = response.json()
    orders.extend(body["data"])
    page = body["next_page"]
return orders
```
