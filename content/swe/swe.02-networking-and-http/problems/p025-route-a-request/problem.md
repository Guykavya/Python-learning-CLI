# Route a request

A server must decide which function handles `GET /notes/7` (chapter sections 15.1 and 16). Write

```python
route(routes, method, path)    # -> (status, handler, extra)
```

`routes` maps `(method, pattern)` to a handler: `{("GET", "/notes"): list_notes, ("POST", "/notes"): add_note, ("GET", "/notes/{id}"): get_note}`. A pattern may contain **parameters** in braces; `{id}` matches one path segment (one or more characters that are not `/`).

Return a tuple:

| Situation | Result |
|---|---|
| a pattern matches the path **and** has a handler for the method | `(200, handler, params)` where `params` is a dict of the captured parameters (`{"id": "7"}`; `{}` for a fixed path) |
| a pattern matches the path but **no** handler for that method | `(405, None, {"Allow": "GET, POST"})`: the `Allow` header lists the methods that **do** exist for that path, sorted, joined by `", "` |
| no pattern matches the path | `(404, None, {})` |

Details:

- The method is case-insensitive. `HEAD` uses the `GET` handler when there is no `HEAD` handler.
- When several patterns match the same path, the **most specific** one (fewest parameters) is tried first: `/notes/new` beats `/notes/{id}`. If its methods do not include the wanted one, try the next matching pattern; if none has it, answer `405` with the methods of all matching patterns.
- `/notes/` is not `/notes`: no trailing-slash magic, no `{id}` matching the empty string, and a parameter never matches a `/`.

## Example

```python
routes = {("GET", "/notes"): "list", ("POST", "/notes"): "add", ("GET", "/notes/{id}"): "get"}
route(routes, "GET", "/notes/7")      # (200, "get", {"id": "7"})
route(routes, "DELETE", "/notes")     # (405, None, {"Allow": "GET, POST"})
route(routes, "GET", "/nothing")      # (404, None, {})
```
