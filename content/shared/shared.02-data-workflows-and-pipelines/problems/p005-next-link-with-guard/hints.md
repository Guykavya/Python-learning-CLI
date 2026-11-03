## Hint 1

Two questions drive the loop: "which URL do I request next?" and "how many pages have I
requested so far?" What does `response.links.get("next")` give when there is no next link?
If you use `for page_number in range(1, max_pages + 1)`, the loop can never make more than
`max_pages` requests. Where in the loop do you `return`, and what does it mean if the loop
finishes without returning?

## Hint 2

```
url = path
for page_number in 1 .. max_pages:
    response = client.get(url); raise_for_status
    add response.json()["orders"]
    nxt = response.links.get("next")
    if nxt is None: return orders           # complete
    url = nxt["url"]
# the loop ran out while a next link was still there
raise TooManyPagesError(f"more than {max_pages} pages ...")
```
