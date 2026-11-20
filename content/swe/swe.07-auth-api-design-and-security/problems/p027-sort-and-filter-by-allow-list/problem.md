# Sort and filter by allow-list

Chapter section 10.4 and "Try it: the sort oracle". Query parameters tempt developers to build SQL from them, or to pass them straight to the database layer. Never accept a column name, an operator or a filter field because the client typed it. If `?sort=secret_note` or `?sort=password_hash` is accepted, an attacker learns hidden data from the **order** of the results, even though the field is never returned. Accept only values from a list **you** wrote, and refuse everything else.

`starter.py` gives you the three allow-lists and the error class. Write `parse_listing(params: dict) -> dict` in `solution.py`. `params` holds the raw query parameters as text (`{"sort": "total", "limit": "5"}`). Return a clean dictionary `{"sort": ..., "status": ..., "limit": ...}`:

- `sort`: one of `SORTS` (`"created"`, `"-created"`, `"total"`); default `"-created"`. Exact match only: no other case, no spaces.
- `status`: one of `STATUSES` (`"pending"`, `"paid"`, `"cancelled"`) or absent (`None`). Exact match.
- `limit`: a whole number from **1 to 100**, written with ASCII digits only; default 20; returned as an `int`. `"0"`, `"101"`, `"-1"`, `"1.5"`, `" 5"`, `"abc"`, `""` and non-ASCII digits (Python's `"٣".isdigit()` is true!) are all errors.
- Any **other** parameter name (`owner_id`, `offset`, `password_hash__startswith`) is an error too: scope first, filter second, and a client may never widen the query.

On any error raise `ListingError` (its `status` is 400). The message must **name the parameter** and **list what is allowed**, so the client can fix the request: for example `invalid sort 'secret_note'; allowed sort values: -created, created, total`. For `limit` say that it must be a whole number from 1 to 100.

## Example

```python
parse_listing({})                                   # {'sort': '-created', 'status': None, 'limit': 20}
parse_listing({"sort": "total", "limit": "5"})      # {'sort': 'total', 'status': None, 'limit': 5}
parse_listing({"sort": "secret_note"})              # ListingError: invalid sort 'secret_note'; allowed sort values: -created, created, total
parse_listing({"limit": "500"})                     # ListingError: invalid limit '500'; limit must be a whole number from 1 to 100
```
