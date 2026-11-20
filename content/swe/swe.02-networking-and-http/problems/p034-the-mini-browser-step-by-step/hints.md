## Hint 1

`urlsplit("http://shop.test/go?src=ad")` gives `hostname = "shop.test"`, `path = "/go"` and `query = "src=ad"`. The program prints only host and path.

## Hint 2

Step 1: no cookies yet, so the `send:` line has no `Cookie:` part. The answer is `302` with a `Location` and a `Set-Cookie`: the cookie is stored **before** the redirect is followed.

## Hint 3

`urljoin("http://shop.test/go?src=ad", "/home")` is `http://shop.test/home`. Step 2 sends `GET /home` **with** `Cookie: sid=abc`, gets `200`, and the body `<h1>Welcome</h1>` has 16 characters. The last line prints `final:` and the body.
