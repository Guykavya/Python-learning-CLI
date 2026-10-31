# Censor words and count them with subn

`re.sub` returns the new string. Its twin `re.subn` returns a pair: the new string **and** how
many replacements it made. That count is handy for reports like "3 words censored".

Write `censor(text: str, words: list[str]) -> tuple[str, int]`.

- Replace every **whole-word** occurrence of any word in `words` with `*` repeated as many times
  as the matched text is long.
- Matching ignores case: `"darn"` also censors `"Darn"` and `"DARN"`.
- Whole words only: censoring `"cat"` must not touch `"catalog"` or `"bobcat"`.
- The words are made of letters and digits, but your code should still treat them as plain text
  (use `re.escape`), never as a pattern.
- Return `(new_text, number_of_replacements)`.
- An empty `words` list changes nothing: `(text, 0)`.

**Example**

```python
censor("Darn it, DARN this darned cat!", ["darn", "cat"])
# ('**** it, **** this darned ***!', 3)

censor("nothing to see", [])
# ('nothing to see', 0)
```
