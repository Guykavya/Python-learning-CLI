## Code

```python
text = input()
print(text.upper())
print(text.lower())
print(text.title())
print(text.swapcase())
print(text.casefold())
```

## Things the tests check

- `"Straße".upper()` is `STRASSE`: one character became two.
- `"Straße".lower()` keeps `ß`, but `casefold()` turns it into `ss`. That is the whole point of `casefold`: `"STRASSE"` and `"Straße"` casefold to the same text.
- `title()` treats an apostrophe as a word break, so `it's` becomes `It'S`. The test expects exactly what Python does; problem p025 looks at a better tool.

## Another way

There is none worth using. Writing your own case conversion with `ord` and `chr` only works for English letters and breaks for `ß`, `é` and many others.
