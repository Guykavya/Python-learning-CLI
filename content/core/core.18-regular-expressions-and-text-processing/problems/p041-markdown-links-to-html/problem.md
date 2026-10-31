# Markdown links to HTML

In Markdown, a link is written `[text](url)`. A static-site generator turns it into
`<a href="url">text</a>`. An **image** looks almost the same but starts with `!`:
`![alt](pic.png)`, and must **not** become a link.

Write `md_links(text: str) -> str` that converts every Markdown link in `text` to HTML.

- `text` (between `[` and `]`) is at least one character and contains no `]`.
- `url` (between `(` and `)`) is at least one character and contains no `)` and no whitespace.
- The `(` must come **immediately** after the `]`.
- Images `![alt](src)` are left exactly as they are.
- Everything else in the text is left unchanged. There can be many links per line and many
  lines.

**Example**

```python
md_links("See [the docs](https://docs.python.org) and [PEP 8](pep8.html).")
# 'See <a href="https://docs.python.org">the docs</a> and <a href="pep8.html">PEP 8</a>.'

md_links("![logo](logo.png) [home](/)")
# '![logo](logo.png) <a href="/">home</a>'

md_links("[not a link] (because of the space)")
# '[not a link] (because of the space)'
```
