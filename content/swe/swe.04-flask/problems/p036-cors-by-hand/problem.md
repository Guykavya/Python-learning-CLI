# CORS by hand

Chapter section 20. A page on `https://app.example` may call your API on another origin only if your server **allows** it with CORS headers. CORS is a rule the **browser** enforces; it protects nothing on the server side. In `solution.py` implement it for paths under `/api/`:

- The allowed origins are `app.config["CORS_ORIGINS"]` (default `["https://app.example"]`). Compare with the **exact** string: no `startswith`, no `in`, no wildcard.
- **Every** response under `/api/` carries `Vary: Origin` (the answer depends on the `Origin` header, caches must know).
- For a request with an **allowed** `Origin`, add `Access-Control-Allow-Origin: <that exact origin>` (never `*`) and `Access-Control-Allow-Credentials: true`.
- A **preflight** is an `OPTIONS` request with both an `Origin` header and `Access-Control-Request-Method`. Answer it **204** with an empty body. For an allowed origin add also `Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE`, `Access-Control-Allow-Headers: Content-Type, Authorization` and `Access-Control-Max-Age: 600`.
- An origin that is **not allowed** (or `null`, or missing) gets **no `Access-Control-*` header at all**. The request itself is still processed normally (the browser, not the server, blocks the reply).
- Paths outside `/api/` get no CORS headers.

The route `GET /api/ping` (answers `pong`) and `GET /ping` exist in the starter.

## Example

```text
OPTIONS /api/ping  Origin: https://app.example  Access-Control-Request-Method: POST
   -> 204, Access-Control-Allow-Origin: https://app.example, ...-Allow-Methods: GET, POST, ..., Vary: Origin
GET /api/ping      Origin: https://evil.example  -> 200 pong, no Access-Control-* headers, Vary: Origin
```
