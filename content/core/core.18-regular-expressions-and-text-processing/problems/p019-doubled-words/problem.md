# Backreferences: find doubled words

A classic typo is a word typed twice: "Paris in the the spring". The eye skips it, especially
across a line break. A **backreference** finds it: `\1` means "the same text that group 1
just matched".

Write `doubled_words(text: str) -> list[str]` in `solution.py`.

- A *word* is a run of `\w` characters (letters, digits, `_`).
- A doubled word is a word followed by whitespace (spaces, tabs or newlines) and then the
  **same word again**, compared **ignoring case**.
- Both copies must be **whole** words: `the theory` is not a doubled word, and neither is the
  `is is` hiding in `this is`.
- Return the doubled words in the order they appear, spelled as the **first** copy is spelled.
  A word typed three times (`go go go`) is reported once.

**Example**

```python
doubled_words("Paris in the the spring")      # ['the']
doubled_words("The the cat sat on on the mat") # ['The', 'on']
doubled_words("this is the theory")            # []
doubled_words("a line ending in\nin the next") # ['in']
```
