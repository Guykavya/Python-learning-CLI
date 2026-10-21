# URL slugs with keyword-only options

A **slug** is the readable part of a web address, like `functions-in-python` in
`example.org/blog/functions-in-python`. Write

```python
make_slug(text, /, *, sep="-", max_length=None)
```

that returns the slug of `text`:

1. Lowercase everything.
2. Keep letters and digits (`str.isalnum()`). Every run of **other** characters (spaces,
   punctuation) becomes **one** `sep`.
3. No `sep` at the start or end.
4. If `max_length` is given, cut the slug to at most that many characters, then remove any `sep`
   left dangling at the end.

`text` is positional-only; `sep` and `max_length` are keyword-only.

**Examples**

```python
make_slug("Functions in Python!")             # "functions-in-python"
make_slug("  Hello,   World  ")               # "hello-world"
make_slug("Top 10 Tips", sep="_")             # "top_10_tips"
make_slug("Functions in Python", max_length=12)   # "functions-in"
make_slug("Functions in Python", max_length=10)   # "functions"
make_slug("!!!")                              # ""
```
