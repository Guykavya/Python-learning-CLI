# Extract hashtags and mentions

Social-media text is full of `#hashtags` and `@mentions`. Pulling them out looks easy until
you meet e-mail addresses (`kavya@example.com` is not a mention) and text like `C#` or `a#b`.

Write `tags(text: str) -> dict[str, list[str]]` in `solution.py` that returns
`{"hashtags": [...], "mentions": [...]}`.

Rules:

- A **hashtag** is `#` followed by one or more word characters (letters, digits, `_`).
  A **mention** is the same with `@`.
- The `#` or `@` must **not** come straight after a word character. So `a#b`, `C#9` and
  `kavya@example.com` contain no tags. After a space, punctuation, a bracket or at the start of
  the text it is fine.
- The tag ends at the first character that is not a word character: `#python!` is `python`.
- Return the names **without** the `#` / `@`, in order of first appearance, each only once.
- Hashtags ignore case: return them **lower-cased**, and `#Python` and `#python` are the same tag.
  Mentions keep their case exactly (`@Ana` and `@ana` are different users).
- Always return both keys, even when a list is empty.

**Example**

```python
tags("Loving #Python and #regex! cc @kavya_b, @Ravi #python")
# {'hashtags': ['python', 'regex'], 'mentions': ['kavya_b', 'Ravi']}

tags("mail me: kavya@example.com, C# is fine, #")
# {'hashtags': [], 'mentions': []}
```
