# A case-insensitive key for dicts

HTTP header names are case-insensitive: `Content-Type` and `content-type` are the same header.
Make a key class that works that way inside a normal dict.

Write `HeaderName(text)` in `solution.py`:

- `h.text` keeps the original text exactly as given.
- Two `HeaderName`s are equal when their texts are equal ignoring case. Use `str.casefold()`
  (it handles cases like German `ß` correctly; `.lower()` does not).
- They must be usable as dict keys and in sets: equal keys must have equal hashes.
- Comparing with a non-`HeaderName` (even a plain `str`) is `False`.
- `repr(h)` is `HeaderName('Content-Type')`; `str(h)` is the original text.

**Example**

```python
d = {HeaderName("Content-Type"): "text/html"}
print(d[HeaderName("CONTENT-TYPE")])     # text/html
d[HeaderName("content-type")] = "json"
print(len(d))                            # 1
print(HeaderName("Content-Type").text)   # Content-Type
```
