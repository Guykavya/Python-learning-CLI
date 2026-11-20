## Hint 1

Open your socket server from swe.02 and look at the functions: which of them would you *not* write again if a library did it? Make a list, then match it to the five points.

## Hint 2

For each point write two short sentences: "In the raw server I ...", "In Flask I ...". Keep a concrete example of each (`@app.route`, `request.form`, `return "text", 404`, `abort`, `test_client()`).

## Hint 3

```text
routing   | if/elif on path     | @app.route + converters + url_for
request   | split bytes         | request.args / form / get_json
response  | status line + len   | return value -> Response
errors    | own 404/500 code    | router 404/405, error handlers
testing   | real socket         | test_client()
not removed: validation, authN/authZ, security, data design
```
