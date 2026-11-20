# K most frequent words

Write `top_k_frequent(words, k)`. It counts the words and returns a **list** of the `k` words that occur most often.

The order of the result is fixed:

1. the word with the **highest count** first;
2. words with the **same count** in **alphabetical order** (Python's normal string order: `"apple" < "pear"`, and capital letters come before small ones: `"Zoo" < "ant"`).

Rules:

- `k <= 0` gives `[]`. If `k` is larger than the number of **different** words, return all of them, in the same order.
- `words` is any iterable of strings (a list, a tuple, a generator); it can be empty.
- Words are compared exactly as they are (no lower-casing, no stripping).

## Example

```python
>>> top_k_frequent(["i", "love", "leetcode", "i", "love", "coding"], 2)
['i', 'love']
>>> top_k_frequent(["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4)
['the', 'is', 'sunny', 'day']
>>> top_k_frequent(["b", "a", "b", "a", "c"], 2)       # b and a both occur twice: a comes first
['a', 'b']
```

## Constraints

- `0 <= len(words) <= 2 * 10**5`; the number of different words can be up to the same number.
- Better than sorting all the different words when `k` is small: aim for `O(n + m log k)`, where `m` is the number of different words. A sort of everything (`O(m log m)`) is accepted by the tests, but a heap is the point of the module.

## Think about

A word with a higher count must come **first**, but a heap hands out the **smallest** key first. How can the key `(count, word)` be changed so that "bigger count" becomes "smaller key", while "smaller word" still wins a tie?
