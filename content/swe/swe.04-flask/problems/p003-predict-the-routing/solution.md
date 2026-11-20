## Approach

Trace each request through the rule map.

```text
1: 308 http://localhost/about/
2: 200 about
3: 404
4: 302 /new
5: 301 /new
6: 404
7: 405
8: 200 saved
```

- **1.** The rule is `/about/` (with a slash). A request without the slash gets a **308** redirect to the canonical URL. The test client shows the `Location` as a full URL (`http://localhost/about/`); the redirects you write yourself with `redirect(url_for(...))` keep the plain path.
- **2.** The exact rule: 200.
- **3.** The rule is `/contact` (without a slash); `/contact/` matches nothing, so 404.
- **4, 5.** `redirect()` sends 302 unless you pass `code=`. `url_for("new")` is `/new`.
- **6.** `x` is not digits, the `int` converter does not match: 404.
- **7.** `/submit` exists, but only for POST: **405 Method Not Allowed** (with an `Allow: OPTIONS, POST` header).
- **8.** The POST works.

Real output of the program, run with Flask 3.1.3.

## Complexity

Not applicable; this is a reading exercise.

## Another way

Instead of predicting, print `app.url_map`: it lists every rule, its methods and its endpoint, which answers most routing questions at once.
