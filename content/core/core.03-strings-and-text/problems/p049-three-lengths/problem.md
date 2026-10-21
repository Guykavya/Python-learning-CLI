# Three lengths of one string

Run this in the REPL (copy it exactly; the third string uses a combining accent):

```python
flag = "🇮🇳"
family = "👨‍👩‍👧"
word = "café"
for s in (flag, family, word):
    print(s, len(s), len(s.encode("utf-8")))
```

A user sees *one* flag, *one* family and *four* letters. Python reports different numbers.

Explain in your own words, in `answer.md`:

1. The three different meanings of "length" for a piece of text, and which one `len()` measures.
2. Why each of the three strings has the `len()` and byte count it has.
3. A real situation where each kind of length is the right one to use (for example: a database column limited in bytes, a tweet-style limit, cutting a preview for display).
4. What can go wrong if you cut a string with a slice like `s[:10]` to make a preview, and what goes wrong if you cut UTF-8 **bytes** at a fixed position.
5. What `unicodedata.normalize("NFC", word)` would change, and why it cannot help with the flag or the family.
