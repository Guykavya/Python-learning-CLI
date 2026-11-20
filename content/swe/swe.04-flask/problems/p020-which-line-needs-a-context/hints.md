## Hint 1

For each line, name the context it needs and the context the function pushes. `app.config` is a normal attribute of the object `app`: no context is involved.

## Hint 2

The **application context** provides `current_app` and `g`. The **request context** provides `request`, `session` and (with the app context) the information `url_for` needs: the host and the script root. An app context alone knows no host.

## Hint 3

```text
1 app.config            -> no context needed
2 current_app, none     -> error
3 current_app, app ctx  -> ok
4 request, app ctx only -> error (no request)
5 request, request ctx  -> ok
6 url_for, none         -> error
7 url_for, app ctx      -> error: no host to build a URL from (unless SERVER_NAME is configured)
8 g, app ctx            -> ok
9 session, app ctx      -> error (session needs a request)
10 url_for, request ctx -> ok
```
