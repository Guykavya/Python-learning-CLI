# Word boundaries: count a whole word

`"the" in text` also finds the `the` inside `theme` and `other`. A **word boundary** `\b`
fixes that: it matches at a position (it uses up no characters) where a word character
(`\w`: letter, digit or `_`) meets a non-word character or the edge of the string.

Write `count_word(text: str, word: str) -> int` in `solution.py`.

- Count how many times `word` appears in `text` as a **whole word**.
- Ignore case: `The`, `THE` and `the` all count for `"the"`.
- `word` always starts and ends with a letter or digit, but it may contain regex special
  characters in the middle, for example `"node.js"` or `"c+d"`. They must be matched literally.
- A hyphen is not a word character, so `well` is a whole word inside `well-known`.
  An underscore **is** a word character, so `the` is not a whole word inside `the_end`.

**Example**

```python
count_word("The theme of the other THE", "the")         # 3
count_word("node.js, nodexjs and NODE.JS", "node.js")   # 2
count_word("well-known well", "well")                   # 2
count_word("the_end", "the")                            # 0
```

In the first line: `The` (yes), `theme` (no), `the` (yes), `other` (no), `THE` (yes).
