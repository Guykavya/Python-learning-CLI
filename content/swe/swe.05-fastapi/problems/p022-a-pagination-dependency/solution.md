## Approach

```python
def page_params(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page:
    return Page(limit=limit, offset=offset)


Pagination = Annotated[Page, Depends(page_params)]


def paginate(data, page: Page):
    return {
        "items": data[page.offset:page.offset + page.limit],
        "total": len(data),
        "limit": page.limit,
        "offset": page.offset,
    }


@app.get("/tasks")
def list_tasks(page: Pagination):
    return paginate(TASKS, page)
```

(`/users` and `/tags` are the same with their own list.)

FastAPI reads `page_params`'s parameters from the query string of **every** request whose endpoint asks for `Pagination`, validates them, calls `page_params` and passes the `Page` it returns. The rules exist in one place, so changing the maximum to 50 is a one-line change, and the docs show the same two parameters on all three endpoints.

Example: `GET /users?limit=3&offset=10`. `page_params` returns `Page(limit=3, offset=10)`; `USERS[10:13]` is `["user 11", "user 12"]` (slicing past the end just stops); `total` is 12.

The override test shows why one dependency is worth it: replacing `page_params` once changes the behaviour of all three endpoints. A test (or a future feature such as "admins get bigger pages") has one handle to turn.

## Complexity

O(limit) per request for the slice (O(1) for the checks).

## Another way

A class dependency (section 9.4): `class Pagination: def __init__(self, limit: Annotated[int, Query(ge=1, le=100)] = 10, offset: ...)` with a `slice(items)` method, used as `page: Annotated[Pagination, Depends()]`. The rules and the slicing then live together in one class.
