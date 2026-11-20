## Hint 1

Which hook runs *before* the view, so that the view can read the id from `g`? Which hook gets the finished response as its argument?

## Hint 2

`re.fullmatch(pattern, text)` returns `None` unless the **whole** text matches; `re.match` only checks the start, which would let `abc def` through. An `after_request` function **must return** the response.

## Hint 3

```text
VALID = re.compile("[A-Za-z0-9_-]{1,64}")

@app.before_request
def set_id():  g.request_id = header if VALID.fullmatch(header) else uuid4().hex

@app.after_request
def add_headers(response):
    response.headers[...] = ...   (three headers)
    return response
```
