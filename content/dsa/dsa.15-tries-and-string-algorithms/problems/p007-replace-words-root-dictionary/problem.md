# Replace words (root dictionary)

A search engine shortens every word to its **root** before indexing, so that `cattle` and `catalog` are both filed under `cat`. Write `replace_words(roots, sentence)` (chapter section 7):

- `roots` is a list of root words;
- `sentence` is words separated by single spaces;
- replace every word by the **shortest** root that is a prefix of it; leave words with no such root unchanged. Return the new sentence, words separated by single spaces.

## Example

```python
>>> replace_words(["cat", "bat", "rat"], "the cattle was rattled by the battery")
'the cat was rat by the bat'
>>> replace_words(["a", "aa", "aaa"], "aadsfasf absbs bbab cadsfafs")
'a a bbab cadsfafs'
>>> replace_words(["ab", "abc"], "abcd ab a")
'ab ab a'
>>> replace_words([], "nothing changes")
'nothing changes'
```

In the second example `a` and `aa` both start `aadsfasf`; the shortest, `a`, wins. In the last one, the word `a` is shorter than every root, so it stays.

## Constraints

- Up to 10**4 roots of up to 100 letters; sentences of up to 10**5 words of up to 300 letters; lowercase letters.
- A word must cost `O(min(len(word), longest root))`.

## Think about

1. Walking a word through a trie of roots, where do you stop to get the **shortest** root?
2. What if the walk breaks before any root ends? What if the word ends before any root ends?
3. Why is `word[:k] in roots` for `k = 1, 2, ...` slower, even though set lookups are `O(1)`?
