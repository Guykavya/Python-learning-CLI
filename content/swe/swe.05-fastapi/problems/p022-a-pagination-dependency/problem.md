# A pagination dependency

Chapter sections 3.3 (`Query` constraints), 9.1 (dependencies) and 9.2 (reuse with a type alias).

Three list endpoints, `/tasks`, `/users` and `/tags`, all take the same two query parameters, `limit` and `offset`, with the same rules. Writing the rules three times means three places to forget one. Write them **once**, in a dependency:

1. `page_params(limit, offset)` reads the two query parameters and returns a **`Page`** object (the starter defines `Page` with fields `limit` and `offset`):
   - `limit`: an `int` from 1 to 100, default **10**;
   - `offset`: an `int` ≥ 0, default **0**.
   Use `Annotated[int, Query(ge=..., le=...)]` so that a bad value is a 422 before your code runs.
2. A type alias **`Pagination = Annotated[Page, Depends(page_params)]`**.
3. The three endpoints take `page: Pagination` and return the slice of their list:

```json
{"items": [...], "total": 25, "limit": 10, "offset": 0}
```

`total` is the length of the **whole** list, `items` is `data[offset:offset + limit]`.

The data is in the starter: `TASKS` (25 strings), `USERS` (12) and `TAGS` (5).

## Example

```text
GET /tasks                   -> {"items": ["task 1", ..., "task 10"], "total": 25, "limit": 10, "offset": 0}
GET /users?limit=3&offset=10 -> {"items": ["user 11", "user 12"], "total": 12, "limit": 3, "offset": 10}
GET /tags?offset=50          -> {"items": [], "total": 5, "limit": 10, "offset": 50}
GET /tasks?limit=0           -> 422, loc ["query", "limit"], type "greater_than_equal"
GET /tags?limit=101          -> 422, loc ["query", "limit"], type "less_than_equal"
```

One test replaces `page_params` with `app.dependency_overrides[page_params]` and checks that **all three** endpoints obey it: that is how you prove there is one source of truth.
