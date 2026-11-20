## Hint 1

Sort the requests into two groups first. A request with `Access-Control-Request-Method` is a **preflight**: the middleware answers it itself and the endpoint never runs. A request without it is a normal request: it goes to the endpoint, and the middleware only **adds headers** to the response on the way out. Which group can produce a 400?

## Hint 2

For a normal request the middleware never changes the status: the endpoint's 200 stays a 200. It adds `Access-Control-Allow-Origin` only if the `Origin` is in `allow_origins`. For a preflight it checks the origin **and** the method against the lists; any failure gives **400** (`Disallowed CORS ...`). The allow-origin header is put on a preflight answer whenever the origin is allowed, even if something else failed.

## Hint 3

```text
1  simple,    origin allowed            -> 200, header = the origin
2  simple,    origin not allowed        -> 200 (endpoint ran), no header
3  preflight, origin ok, POST ok        -> 200, header = the origin
4  preflight, origin ok, DELETE not ok  -> 400, header = the origin (origin itself was fine)
5  preflight, origin not ok             -> 400, no header
```
