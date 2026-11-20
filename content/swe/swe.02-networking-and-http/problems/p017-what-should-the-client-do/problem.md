# What should the client do?

Chapter section 10.4: a status code tells the client what to do next. Write

```python
client_action(status, headers, now=None)
```

`headers` is a dict (any capitalisation of the names). `now` is a timezone-aware `datetime` (default: the current UTC time; tests pass a fixed one). Return one of these strings:

| Situation | Result |
|---|---|
| `2xx` and `304` | `"use"` |
| `301`, `302`, `303`, `307`, `308` with a `Location` header | `"follow:<location>"` (a redirect with no `Location`: `"give-up"`) |
| `429` or `503` **with** a usable `Retry-After` | `"wait:<seconds>"` (an integer) |
| `429` or `503` without `Retry-After`, or with garbage in it | `"retry"` |
| `408`, `500`, `502`, `504` | `"retry"` |
| `401` | `"log-in"` |
| `400`, `404`, `405`, `409`, `410`, `415`, `422` | `"fix-request"` |
| anything else (`403`, `418`, `1xx`, `501`, ...) | `"give-up"` |

`Retry-After` is either a **number of seconds** (`"30"`) or an **HTTP date** (`"Sat, 07 Nov 2026 10:00:30 GMT"`). For a date, the wait is the time from `now` to that date, rounded **up** to whole seconds; a date in the past gives `0`. Use `email.utils.parsedate_to_datetime`.

## Example

```python
client_action(200, {})                                   # "use"
client_action(301, {"location": "/new"})                 # "follow:/new"
client_action(503, {"Retry-After": "30"})                # "wait:30"
client_action(404, {})                                   # "fix-request"
client_action(401, {})                                   # "log-in"
```
