## Approach

Apply the conversion table of section 5.1 to each view.

```text
1: 200 | text/html; charset=utf-8 | hello
2: 201 | text/html; charset=utf-8 | created
3: 418 | text/plain | teapot
4: 200 | application/json | {"n":3,"ok":true}
5: 204 | text/html; charset=utf-8 |
```

- **1, 2.** Strings become an HTML response with UTF-8; the tuple's second item sets the status.
- **3.** The headers dict is applied after the defaults, so `Content-Type: text/plain` wins, **exactly as written**: there is no `; charset=utf-8` because you did not write it.
- **4.** A dict is converted with `jsonify` (Flask's JSON provider). The provider sorts the keys and writes the **compact** form (no spaces) unless the app is in debug mode; the response ends with a newline, which `.strip()` removed.
- **5.** The empty body with 204 is fine: 204 means "success, no content". Flask still attaches its default content type; clients ignore it for 204.

Real output of the program, run with Flask 3.1.3.

## Complexity

Not applicable; this is a reading exercise.

## Another way

`print(app.make_response(value).headers)` for any value shows the response Flask builds from it.
