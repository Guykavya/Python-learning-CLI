## Hint 1

List the checks a request must pass, in order, and the status each failure gets. Which checks are needed by `POST`, which by `PATCH` and `DELETE`? Can some be shared in small helper functions?

## Hint 2

Helpers keep the four routes short: `json_object()` returns the dict or an error response; `owned_post(id)` returns the post or an error response (404, then 403); `validate(data, partial)` returns the `fields` dict. For PATCH, a field that is **not in the dict** is left alone: check `"title" in data`.

## Hint 3

```text
POST:   g.user? -> json_object -> validate(full) -> create -> 201 + Location
PATCH:  g.user? -> json_object -> owned_post (404, 403) -> validate(partial) -> update given keys -> 200
DELETE: g.user? -> owned_post -> delete -> 204
every error: api_error(status, code, message[, fields=...])
```
