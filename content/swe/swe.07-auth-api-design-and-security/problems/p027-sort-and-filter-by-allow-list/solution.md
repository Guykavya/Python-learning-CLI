## Approach

```python
def _allowed(values):
    return ", ".join(sorted(values))


def parse_listing(params: dict) -> dict:
    unknown = sorted(set(params) - PARAMS)
    if unknown:
        raise ListingError(f"unknown parameter {unknown[0]!r}; allowed parameters: {_allowed(PARAMS)}")
    sort = params.get("sort", "-created")
    if sort not in SORTS:
        raise ListingError(f"invalid sort {sort!r}; allowed sort values: {_allowed(SORTS)}")
    status = params.get("status")
    if status is not None and status not in STATUSES:
        raise ListingError(f"invalid status {status!r}; allowed status values: {_allowed(STATUSES)}")
    raw = params.get("limit", "20")
    if not (raw.isascii() and raw.isdigit()) or not 1 <= int(raw) <= 100:
        raise ListingError(f"invalid limit {raw!r}; limit must be a whole number from 1 to 100")
    return {"sort": sort, "status": status, "limit": int(raw)}
```

The rule is an **allow-list**: a value passes only if it is in a set you wrote. A block-list ("no semicolons, no `DROP`") always misses something. After this function, the rest of the code never sees raw client text: `sort` is one of three constants, which can be mapped to a column name (`{"created": "created_at", "total": "total_cents"}`) and put into the SQL text safely, as the chapter's `list_orders` does. `limit` is a real `int` inside a hard range, so nobody can ask for a million rows. The error message lists the allowed values: that helps honest clients and costs nothing, because the list is public API documentation anyway. `isascii()` before `isdigit()` matters: `"٣".isdigit()` is `True`, and `"²".isdigit()` is `True` while `int("²")` raises `ValueError`.

## Complexity

O(number of parameters + length of `limit`).

## Another way

In FastAPI, the same rules fit a Pydantic model or `Literal`/`Enum` types with `Query(ge=1, le=100)`: the framework then answers 422 with its own error format. Writing the function by hand shows what that machinery does, and it can be tested without a web server. Keep the unknown-parameter check in either case: frameworks ignore extra parameters by default.
