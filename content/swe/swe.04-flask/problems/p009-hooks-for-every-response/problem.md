# Hooks for every response

Chapter sections 5.5 and 5.6. Some work must happen for **every** request: this is what `before_request` and `after_request` are for. In `solution.py` write `create_app(test_config=None)` with:

- A route `GET /whoami` that returns the current request id as plain text (read from `g.request_id`).
- A `before_request` hook that sets `g.request_id`: the incoming `X-Request-ID` header **if it is valid**, otherwise a new `uuid.uuid4().hex`. A valid id is 1 to 64 characters from `A-Z a-z 0-9 _ -` (use `re.fullmatch`). Never trust the header blindly: it ends up in your logs and in your response.
- An `after_request` hook that adds to **every** response, including errors:
  - `X-Request-ID`: the same id,
  - `X-Content-Type-Options: nosniff`,
  - `X-Frame-Options: DENY`.

The hooks must also cover Flask's own error pages (404, 405).

## Example

```text
GET /whoami                        -> 200 <32 hex characters>   X-Request-ID: <the same>
GET /whoami  X-Request-ID: abc-1   -> 200 abc-1                 X-Request-ID: abc-1
GET /whoami  X-Request-ID: bad id! -> 200 <a new 32-hex id>
GET /missing                       -> 404, with the three headers
```
