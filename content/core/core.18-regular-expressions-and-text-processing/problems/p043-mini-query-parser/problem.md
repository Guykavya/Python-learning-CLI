# Mini search-query parser

Search boxes on GitHub, Gmail and many shops accept **filters** mixed with free words:

```text
author:"Jane Doe" tag:py tag:re free words
```

Write `parse_query(q: str) -> dict[str, list[str]]` that turns such a query into a dict.

The query is a sequence of **terms** separated by whitespace. A term is one of:

- **filter**: `key:value`, where `key` is one or more word characters (`\w`), directly followed
  by `:` and then directly by a value. Keys are case-insensitive: store them in lower case.
- **free word**: anything else. Free words go under the key `"_"`.

A **value** (of a filter or a free word) is either:

- a quoted phrase `"..."` (no `"` inside): the quotes are removed, the inside is kept exactly
  (spaces too, and it may be empty), or
- a run of non-whitespace characters.

Rules for the result:

- Values are kept in the order they appear; a key used several times collects all its values.
- Keys appear in the dict in the order they are first seen; only keys that occur are present.
- A key followed by nothing (like `tag:` before a space or at the end) is not a filter: the whole
  term, colon included, is a free word.
- A quote that is never closed is just an ordinary character: `"Jane` is a free word `"Jane`.
- An empty or all-whitespace query gives `{}`.

**Example**

```python
parse_query('author:"Jane Doe" tag:py tag:re free words')
# {'author': ['Jane Doe'], 'tag': ['py', 're'], '_': ['free', 'words']}

parse_query('"exact phrase" Lang:Python tag:')
# {'_': ['exact phrase', 'tag:'], 'lang': ['Python']}
```
