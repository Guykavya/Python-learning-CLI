## Approach

Follow the loop: each pass of the `for` is one request.

| Round trip | What happens |
|---|---|
| 1 | parse the URL (host `shop.test`, path `/go`; the query `src=ad` is separate); send `GET /go` with no cookie; the answer is `302` with `Location: /home` and `Set-Cookie: sid=abc`; the cookie is stored; `urljoin` makes `http://shop.test/home`; `continue` |
| 2 | parse; send `GET /home` **with** `Cookie: sid=abc`; status `200`; no `Set-Cookie`, not a redirect: print the body length (16 characters) and return the body |

Output (checked by running the code):

```text
1. parse: host=shop.test path=/go
1. send: GET /go
1. status: 302
1. cookie stored: sid
1. follow: http://shop.test/home
2. parse: host=shop.test path=/home
2. send: GET /home Cookie: sid=abc
2. status: 200
2. body: 16 bytes
final: <h1>Welcome</h1>
```

The `send:` line shows only `parts.path`, so the query `?src=ad` is not sent in this mini browser: the chapter's `mini_fetch` builds the request target as `path + "?" + query`; this version simplifies, and it **would** be a bug in a real client (the server would never see `src=ad`). The cookie travels with the **second** request, because it was learnt from the first answer. A server redirecting to itself would loop until `range(1, 6)` ends: the function would stop after 5 round trips and return `None` (a real browser stops at about 20 redirects with an error).

## Complexity

Not applicable.

## Another way

Add a `print` of the dictionary `cookies` after each answer to see the state. Then try the same URL with a `Location` that is an absolute URL on another host, and think about whether the cookie should be sent there (it should not: cookies belong to a host, as in problem 20).

## Why it matters

Redirects and cookies together are how logins work: the first answer sets the session cookie, the redirect brings you to the page that needs it.
