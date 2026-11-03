## Hint 1

Unlike page numbers, there is no "first cursor" value you can send. So what does the very first
`params` dict look like, and how does it change after each answer? Which checks end the loop,
and how do you read a key that may not be in the dict without a `KeyError`?

## Hint 2

```
params = {"limit": limit}                 # no cursor yet
loop:
    response = client.get("/v1/orders", params=params); raise_for_status
    body = response.json()
    add body["items"]
    cursor = body.get("next_cursor")
    if cursor is None: return
    params = {"limit": limit, "cursor": cursor}
```
