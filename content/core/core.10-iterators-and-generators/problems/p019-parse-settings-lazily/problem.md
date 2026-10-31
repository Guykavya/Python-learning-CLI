# Parse key=value settings lazily

A settings file is a list of text lines (a list or a generator of strings):

```text
# app settings
name = Kavya

theme=dark
   # another comment
url = https://site.org/?page=2
```

Write a **generator function** `parse_settings(lines)` in `solution.py`. For each useful line,
it yields a tuple `(key, value)`.

- Skip **blank** lines (only spaces, or nothing).
- Skip **comment** lines: the first character that is not a space is `#`.
- Split a line at the **first** `=` only. The value may contain more `=` signs.
- Remove spaces around the key and around the value. The value may be empty.
- A useful line with no `=` is an error: raise `ValueError` with a message that contains the
  **line number** (the first line is line 1; blank and comment lines count too), for example
  `"line 4: missing '='"`.

Because it is a generator, the pairs before the bad line are still yielded first.

**Example**

```python
lines = ["# app settings", "name = Kavya", "", "theme=dark",
         "   # another comment", "url = https://site.org/?page=2"]
list(parse_settings(lines))
# [('name', 'Kavya'), ('theme', 'dark'), ('url', 'https://site.org/?page=2')]

dict(parse_settings(["a = 1", "b = 2"]))   # {'a': '1', 'b': '2'}
```
