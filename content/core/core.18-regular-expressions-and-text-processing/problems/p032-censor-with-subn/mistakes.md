- Replacing with a fixed string like `"****"`: `"no"` would get four stars. The length depends on
  the match, so the replacement must be a function.
- `r"\b" + "|".join(words) + r"\b"` without a group: `\bdarn|cat\b` means `\bdarn` **or** `cat\b`,
  so `"darned"` gets censored.
- Forgetting `re.escape`: a word with `.` would match any character there.
- Forgetting `re.IGNORECASE` and lower-casing the text instead: the returned text must keep the
  original case of everything that is not censored.
- Not checking for an empty list: the empty alternation matches the empty string at every word
  boundary, so stars appear everywhere and the count is wrong.
- Using `sub` and counting with `text.count(word)`: that counts parts of words and ignores case.
