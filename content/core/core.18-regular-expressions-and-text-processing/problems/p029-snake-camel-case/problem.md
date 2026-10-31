# snake_case and camelCase conversion

Python names use `snake_case`, JSON from a JavaScript API uses `camelCase`. Converting between
them is a classic regex job, and acronyms (`HTTPServer`) are what make it interesting.

Write two functions in `solution.py`.

1. `to_snake(name: str) -> str`
   - Put `_` at every word boundary inside the name, then lower-case everything.
   - A boundary is before a capital that follows a lower-case letter or a digit:
     `camelCase` → `camel_case`, `version2Update` → `version2_update`.
   - Inside a run of capitals, the **last** capital starts a new word when a lower-case letter
     follows it: `HTTPServer` → `http_server`, `getHTTPResponseCode` → `get_http_response_code`.
   - A name that is already snake_case comes back unchanged. Existing underscores stay.
2. `to_camel(name: str) -> str`
   - The input is snake_case (lower-case letters, digits, underscores).
   - Every `_` that follows a letter or digit and is followed by a letter or digit is removed,
     and the character after it becomes upper-case (a digit stays a digit).
   - Leading underscores are kept: `_private_var` → `_privateVar`.

**Example**

```python
to_snake("HTTPServer")            # 'http_server'
to_snake("getHTTPResponseCode")   # 'get_http_response_code'
to_snake("already_snake")         # 'already_snake'
to_camel("get_http_response_code")  # 'getHttpResponseCode'
to_camel("_private_var")            # '_privateVar'
```
