# Word break

Write `word_break(s, words)` that returns `True` if the string `s` can be cut into pieces that are all in the list `words` (each word may be used any number of times), and `False` otherwise (chapter section 5).

## Example

```python
>>> word_break("leetcode", ["leet", "code"])
True
>>> word_break("applepenapple", ["apple", "pen"])          # apple is used twice
True
>>> word_break("catsandog", ["cats", "dog", "sand", "and", "cat"])
False
>>> word_break("", ["a"])                                  # the empty string needs no cut
True
```

## Constraints

- `0 <= len(s) <= 1000`, `1 <= len(words) <= 200`, each word has 1 to 20 lowercase letters.
- The test raises the recursion limit to 5000 for the large inputs, so a **memoised** recursion over positions is allowed. A recursion **without** a memo is exponential: `"a" * 1000 + "b"` with the words `a, aa, aaa, ...` never finishes.

## Think about

What does `f(i)` mean, and which earlier `f(j)` does it look at? Unlike stairs, the transition looks back at **every** earlier cut point. How can the longest word length make that loop shorter?
