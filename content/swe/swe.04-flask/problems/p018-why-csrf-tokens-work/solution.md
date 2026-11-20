## Approach

Think about who knows what. The browser knows the cookie and sends it for you. The attacker's page knows only the URL and the form fields it writes itself. The token closes the gap because it is something the attacker's page cannot *read*.

See `answer.md` for a model answer and a checklist. The key sentence: **a cookie proves "this browser is logged in"; a CSRF token proves "this request came from our own page".**

Example: the hidden form on `evil.example` can set `to` and `amount`, but when it needs `csrf_token` it has nothing to write: the real value sits in a page that the same-origin policy hides from it.

## Complexity

Not applicable.

## Another way

Check the `Origin` or `Referer` header on unsafe requests: browsers set them and a page cannot change them. Frameworks combine this with tokens. APIs that send a token in an `Authorization` header (not a cookie) are not affected, because the browser never adds that header on its own.
