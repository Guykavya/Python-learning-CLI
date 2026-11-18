# Interleaving string

`s3` is an **interleaving** of `s1` and `s2` if you can split `s3` letter by letter into two subsequences, one equal to `s1` and the other equal to `s2`. In other words, you shuffle the two strings together like two decks of cards, keeping the order inside each deck.

Write `is_interleave(s1, s2, s3)` that returns `True` or `False`.

## Example

```python
>>> is_interleave("aabcc", "dbbca", "aadbbcbcac")
True
>>> is_interleave("aabcc", "dbbca", "aadbbbaccc")
False
>>> is_interleave("", "", "")
True
>>> is_interleave("a", "b", "a")          # a letter of s2 is missing
False
```

In the first example: `aa` from `s1`, `dbbc` from `s2`, `bc` from `s1`, `a` from `s2`, `c` from `s1`.

## Constraints

- `0 <= len(s1), len(s2) <= 300`, `0 <= len(s3) <= 600`, lowercase letters.
- `O(len(s1) * len(s2))` time.

## Think about

A greedy rule ("take from `s1` whenever its next letter fits") fails when both strings offer the same letter: `is_interleave("ab", "ac", "acab")`. So you must try both. After using `i` letters of `s1` and `j` letters of `s2`, how many letters of `s3` have you used? Which state is enough, then, and how many states are there?
