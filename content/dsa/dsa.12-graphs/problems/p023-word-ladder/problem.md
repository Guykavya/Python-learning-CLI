# Word ladder

Turn `begin` into `end` by changing **one letter at a time**; every word in between must be in the list `words`. For example `hit -> hot -> dot -> dog -> cog`. The words are the vertices of a graph, and two words are joined when they differ in exactly one position (chapter section 18, example 1). The fewest steps is a BFS.

Write `ladder_length(begin, end, words)`. It returns the number of **words** in the shortest ladder, counting `begin` and `end` (so `hit -> hot -> dot -> dog -> cog` gives `5`), or `0` if there is no ladder.

Rules:

- All words have the same length and use lowercase letters.
- `end` must be in `words`; if it is not, the answer is `0`.
- `begin` does not have to be in `words`.
- If `begin == end` (and it is in `words`), the answer is `1`.

## Example

```python
>>> ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"])
5
>>> ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log"])
0
```

In the second example `cog` is not in the list.

## Constraints

Up to 12,000 words of length up to 10. Comparing every pair of words is `O(N^2 * L)`: 72 million pairs for 12,000 words, too slow. The tests run such a list in a separate process with a 10-second limit. Find the neighbours of a word without looking at every other word.
