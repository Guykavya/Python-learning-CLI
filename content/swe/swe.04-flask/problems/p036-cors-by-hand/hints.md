## Hint 1

Two kinds of request need different work: the **preflight** (the browser asks "may I?") needs its own answer and the full list of allowed methods; the **real request** only needs the allow-origin header. Which hook sees every response, including the ones of other routes?

## Hint 2

Use `before_request` to answer the preflight early (`make_response("", 204)`), and `after_request` to add headers to everything under `/api/`. `response.headers.add("Vary", "Origin")` adds without removing an existing `Vary`. The decision is `origin in app.config["CORS_ORIGINS"]` (a list membership test is an exact comparison).

## Hint 3

```text
before_request: if path under /api/ and is_preflight: return 204
after_request:  if not /api/: return response
                add Vary: Origin
                if origin in allowed: Allow-Origin = origin, Allow-Credentials = true,
                                      and for a preflight: Methods, Headers, Max-Age
                return response
```
