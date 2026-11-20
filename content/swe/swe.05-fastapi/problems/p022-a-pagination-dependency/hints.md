## Hint 1

A dependency declares parameters exactly like an endpoint does. Where do you put `ge=1, le=100` so that FastAPI checks it for every endpoint that uses `page_params`? (Section 3.3 for `Annotated[int, Query(...)]`, section 9.1 for dependencies.)

## Hint 2

Each endpoint only needs `page: Pagination` in its signature. The slicing is the same three times, so a small helper `paginate(data, page)` that builds the dict keeps the endpoints to one line each.

## Hint 3

```text
page_params(limit: Annotated[int, Query(ge=1, le=100)] = 10,
            offset: Annotated[int, Query(ge=0)] = 0) -> Page

paginate(data, page):
    return {"items": data[page.offset:page.offset + page.limit],
            "total": len(data), "limit": page.limit, "offset": page.offset}

list_tasks(page: Pagination): return paginate(TASKS, page)      # same for users, tags
```
