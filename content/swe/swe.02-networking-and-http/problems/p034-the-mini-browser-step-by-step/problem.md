# The mini browser, step by step

Chapter section 25.1 follows one URL through all the steps. This version has no network: a dictionary `web` plays the servers. It follows **redirects** and keeps **cookies**, and prints each step.

```python
from urllib.parse import urljoin, urlsplit

web = {
    "http://shop.test/go?src=ad": (302, {"Location": "/home", "Set-Cookie": "sid=abc"}, ""),
    "http://shop.test/home": (200, {}, "<h1>Welcome</h1>"),
}


def browse(url):
    cookies = {}
    for step in range(1, 6):
        parts = urlsplit(url)
        print(f"{step}. parse: host={parts.hostname} path={parts.path}")
        cookie = "; ".join(f"{k}={v}" for k, v in cookies.items())
        print(f"{step}. send: GET {parts.path}" + (f" Cookie: {cookie}" if cookie else ""))
        status, headers, body = web[url]
        print(f"{step}. status: {status}")
        if "Set-Cookie" in headers:
            name, _, value = headers["Set-Cookie"].partition("=")
            cookies[name] = value
            print(f"{step}. cookie stored: {name}")
        if status in (301, 302) and "Location" in headers:
            url = urljoin(url, headers["Location"])
            print(f"{step}. follow: {url}")
            continue
        print(f"{step}. body: {len(body)} bytes")
        return body


print("final:", browse("http://shop.test/go?src=ad"))
```

Predict **exactly** what the program prints, line by line (the numbers at the start of each line count the **round trips**). Do not run it.

Write your answer in `answer.txt`.

## How to work

1. Step 1: parse `http://shop.test/go?src=ad`: what are `parts.hostname` and `parts.path`? (The query is **not** part of `path`.)
2. Is a cookie known before the first answer? What does `browse` do when the answer has `Set-Cookie`?
3. For a redirect, `urljoin(url, "/home")` builds the next URL from the current one. Which round trip sends the cookie?

## After you answer

1. Why does the `send:` line of step 1 show `/go` and not `/go?src=ad`? Is that a bug of this mini browser?
2. At which line does the cookie travel to the server for the first time?
3. What would happen if `web` held a `302` that redirected to itself?
