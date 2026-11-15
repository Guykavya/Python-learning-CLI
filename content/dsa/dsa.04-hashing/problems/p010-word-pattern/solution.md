## Approach

Split the sentence into words. If the counts differ, the answer is `NO`. Otherwise check each `(letter, word)` pair
against a forward and a backward dictionary, exactly as in isomorphic strings.

## Code

```python
pattern = input().strip()
words = input().split()

answer = "YES"
if len(pattern) != len(words):
    answer = "NO"
else:
    to_word = {}
    to_letter = {}
    for ch, w in zip(pattern, words):
        if to_word.get(ch, w) != w or to_letter.get(w, ch) != ch:
            answer = "NO"
            break
        to_word[ch] = w
        to_letter[w] = ch
print(answer)
```

## Complexity

O(n + total length of the words): hashing a word costs its length.

## Another way

Map each side to a **pattern of first appearances** and compare: `[pattern.index(c) for c in pattern]` against
`[words.index(w) for w in words]`. That is O(n^2) with `index`; build the first-appearance numbers with a
dictionary to keep it O(n).
