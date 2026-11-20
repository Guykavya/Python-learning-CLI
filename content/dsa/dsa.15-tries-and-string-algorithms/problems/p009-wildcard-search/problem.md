# Wildcard search `.`

A crossword helper stores a word list and answers patterns like `c.t` ("a three-letter word: c, any letter, t"). Write a class `WordDictionary` (chapter section 7, "Words with wildcards"):

- `add_word(word)`: store a word of lowercase letters;
- `search(pattern)`: `True` if some stored word matches `pattern`, where `.` matches **exactly one** letter and every other character must match itself. The word and the pattern must have the **same length**.

## Example

```python
>>> wd = WordDictionary()
>>> for w in ["bad", "dad", "mad", "pad"]:
...     wd.add_word(w)
>>> wd.search("pad"), wd.search(".ad"), wd.search("b..")
(True, True, True)
>>> wd.search("b."), wd.search("..d."), wd.search("x..")
(False, False, False)
>>> wd.search("...")
True
```

`b.` is false: every stored word has three letters, and `.` matches exactly one letter, not "anything".

## Constraints

- Up to 2 * 10**4 words of 1 to 10 letters, and 2 * 10**4 patterns with up to 3 dots.
- A pattern without dots costs `O(len(pattern))`. Comparing the pattern with every stored word is too slow.

## Think about

1. At a `.`, the normal trie walk does not know which edge to follow. What does it do instead, and when does it stop?
2. Which check at the end of the pattern makes `b.` false?
3. Which patterns are the most expensive, and why can a search never visit more nodes than the trie has?
