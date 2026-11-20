# Build URLs without string glue

Chapter section 13.2: pasting strings into a URL breaks as soon as a value contains `/`, `&`, `#`, a space or non-English text. Write

```python
build_url(base, segments, query=None)
```

- `base` is a URL such as `"https://api.example.com/v1"` (a trailing `/` is allowed and removed).
- `segments` is a list of path parts. Each one is turned into text with `str()` and **percent-encoded with `/` also encoded** (`urllib.parse.quote(part, safe="")`), so `"a/b"` stays **one** segment: `a%2Fb`.
- `query` is a dict. Encode it with `urllib.parse.urlencode(..., doseq=True)`: a list value gives one `key=value` pair per item (`tag=a&tag=b`), a space becomes `+`. Keys whose value is `None` are **left out**. If nothing is left, add no `?` at all.
- Result: `base + "/" + segments joined with "/"`, then `"?"` + query if there is one. No segments: just the base.

Non-English text is encoded as UTF-8 bytes (`ça` becomes `%C3%A7a`).

## Example

```python
build_url("https://api.example.com/v1/", ["users", "a/b"], {"q": "x y", "tag": ["a", "b"]})
# 'https://api.example.com/v1/users/a%2Fb?q=x+y&tag=a&tag=b'
build_url("http://h", ["files", "../etc"])
# 'http://h/files/..%2Fetc'      the slash cannot escape the segment
```
