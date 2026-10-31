# finditer with positions

`re.findall` gives you the matched **text**. Often you also need to know **where** each match
is: to highlight it, to cut the string around it, or to report "column 14". `re.finditer`
gives you one `Match` object per match, and `m.span()` is the `(start, end)` pair.

Write `find_all_spans(pattern: str, text: str) -> list[tuple[int, int]]`.

- Return the `(start, end)` of every match of `pattern` in `text`, left to right.
- Matches do not overlap: after a match, the search continues at its `end`.
- **Zero-width matches count too.** A pattern like `\b` or `a*` can match the empty string; such a
  match has `start == end` and must be in the list.
- `text[start:end]` must give back the matched text.

**Example**

```python
find_all_spans(r"\d+", "a1 b22 c333")
# [(1, 2), (4, 6), (8, 11)]

find_all_spans("aa", "aaaa")
# [(0, 2), (2, 4)]           not (1, 3): matches never overlap

find_all_spans(r"\b", "hi yo")
# [(0, 0), (2, 2), (3, 3), (5, 5)]   four word boundaries, all zero-width

find_all_spans("a*", "baa")
# [(0, 0), (1, 3), (3, 3)]
```
