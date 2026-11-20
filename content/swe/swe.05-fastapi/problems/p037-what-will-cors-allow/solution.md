## Approach

Decide for each request whether it is a preflight, then apply the middleware's rules.

```text
1: 200 https://app.example.com
2: 200 none
3: 200 https://app.example.com
4: 400 https://app.example.com
5: 400 none
```

- **1.** A simple GET from the allowed origin. The endpoint runs (200) and the middleware adds `Access-Control-Allow-Origin: https://app.example.com` (the exact origin, not `*`, because `allow_credentials=True`). It also adds `Access-Control-Allow-Credentials: true`.
- **2.** A simple GET from `evil.example`. The middleware does **not** block it: the endpoint runs and answers 200. It just does not add the allow-origin header. The browser then refuses to let the JavaScript of `evil.example` **read** the response. CORS protects the user's browser from leaking data to other sites; it is not a firewall for the server.
- **3.** A preflight for POST from the allowed origin: origin and method are in the lists, so 200 with the allow-origin header (and `Access-Control-Allow-Methods: GET, POST`). The endpoint did not run.
- **4.** A preflight for DELETE: the origin is fine, so the middleware puts the origin header on the answer, but DELETE is not in `allow_methods`, so the answer is **400** with the text `Disallowed CORS method`. The browser needs a successful (2xx) preflight, so the real DELETE is never sent.
- **5.** A preflight from a foreign origin: 400 `Disallowed CORS origin`, no allow-origin header.

Real output of the program, run with FastAPI 0.162.0 (Starlette 1.10.0) and Pydantic 2.14.3.

## Complexity

Not applicable; this is a reading exercise. (The middleware's checks are a set lookup for the method and a list lookup for the origin.)

## Another way

Print all response headers for each request (`dict(r.headers)`) and read the full story: `vary: Origin`, `access-control-allow-credentials`, `access-control-allow-methods`, `access-control-max-age`. Answer to question 3 of "After you answer": without `Access-Control-Request-Method` the middleware treats the `OPTIONS` as a normal request, passes it to the router, and since no route handles `OPTIONS /data`, the answer is **405 Method Not Allowed** (with the allow-origin header added, because the origin is allowed).
