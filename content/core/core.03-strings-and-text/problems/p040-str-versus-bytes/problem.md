# str versus bytes

A student downloads a file of customer names produced by an old Windows program. Their code is:

```python
data = open("names.txt", "rb").read()    # reads raw bytes
text = data.decode("utf-8")
```

It crashes with:

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 3: invalid continuation byte
```

Explain in your own words, in `answer.md`:

1. The difference between `str` and `bytes` in Python, and what `encode` and `decode` do.
2. Why `len("café")` is 4 but `len("café".encode("utf-8"))` is 5.
3. What the error message is telling you, piece by piece.
4. How to fix it properly, and why `errors="ignore"` is not a real fix.
5. What "mojibake" is and how it happens.

Use small examples.
