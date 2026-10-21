# Make the failing tests pass: word_frequency

`test_solution.py` is the specification. Read it carefully, especially the edge cases: the tests
are written so that the obvious first attempt fails in several different ways. Write
`word_frequency(text)` in `solution.py`.

It returns a **dict** that maps each word to how many times it occurs.

- case does not matter: `"The the THE"` counts `"the"` three times;
- punctuation at the **start or end** of a word is dropped, but punctuation **inside** a word
  stays (`"don't"`, `"well-known"`);
- words are separated by any amount of whitespace (spaces, tabs, new lines);
- a "word" that is only punctuation (`"--"`) is not a word and is not counted;
- empty or blank text gives `{}`.

**Examples**

```python
word_frequency("to be or not to be")   # {"to": 2, "be": 2, "or": 1, "not": 1}
word_frequency("Hi, hi! HI.")          # {"hi": 3}
word_frequency("don't stop")           # {"don't": 1, "stop": 1}
word_frequency("")                     # {}
```
