## Hint 1

Separate two things: what the browser **sends** (cookies, automatically) and what a page of another site can **read** (almost nothing). Which of the two does the attacker need?

## Hint 2

A token works because it is sent by *your code in the page*, not by the browser by itself. Where is the token before it is in the request? Who is allowed to read that page?

## Hint 3

```text
1. cookie sent automatically; attacker only needs the side effect
2. token only in the bank's pages; same-origin policy keeps evil.example from reading them
3. Lax: no cookie on cross-site POST; not enough: GET that changes data, same-site attacker, old browsers
4. GET can be triggered by an image or a link, with no way to add a token
```
