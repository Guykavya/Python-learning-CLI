# KMP search

Write `kmp_search(text, pattern)` that returns the sorted list of **all** start positions where `pattern` occurs in `text`, **overlapping** occurrences included, in `O(len(text) + len(pattern))` (chapter section 11).

The empty pattern occurs at every position `0, 1, ..., len(text)` (as with `str.find`, which finds `""` everywhere): return `list(range(len(text) + 1))`.

## Example

```python
>>> kmp_search("abcabcabd", "abcabd")
[3]
>>> kmp_search("aaaaa", "aa")             # overlapping: str.count would say 2
[0, 1, 2, 3]
>>> kmp_search("abababab", "abab")
[0, 2, 4]
>>> kmp_search("abc", "abcd")             # pattern longer than the text
[]
>>> kmp_search("ab", "")
[0, 1, 2]
```

## Constraints

- Texts up to 10**6 characters, patterns up to 10**5; any characters.
- Worst case: repeated pattern like `aaaa...b` in a text of `a`s. The naive search compares almost the whole pattern at every start: `O(n * m)`.

## Think about

1. What does the state `k` mean while you scan the text?
2. After a full match (`k == m`), what must `k` become so that overlapping matches are found and `pattern[k]` is never read past the end?
3. Which special cases come before the main loop?
