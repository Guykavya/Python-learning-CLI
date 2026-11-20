# Count of numbers in a range (merge sort tree or offline)

An exam board keeps the marks of `n` students in roll-number order. Each question is a triple `(l, r, x)`: *how many students with roll numbers in `[l, r)` scored strictly less than `x`?* The marks never change, and all questions are known in advance. Write `count_below(a, queries)` that returns the list of answers, in the order of `queries`. Ranges are **half-open and 0-indexed**.

## Example

```python
>>> a = [5, 1, 4, 2, 8, 3]
>>> count_below(a, [(0, 6, 4), (1, 4, 3), (2, 2, 9), (3, 6, 100), (0, 3, 1)])
[3, 2, 0, 3, 0]
```

`(0, 6, 4)`: the marks below 4 are 1, 2, 3. `(1, 4, 3)`: among `1, 4, 2`, two are below 3.

## Constraints

- Up to 10**5 marks and 10**5 questions; marks and `x` from `-10**9` to `10**9`.
- Answering each question by scanning the range is `O(n)` per question. Aim for `O((n + q) log n)`.

## Think about

1. A segment tree cannot merge "how many below `x`" for a changing `x` directly. Two ways around it (chapter section 17, "What offline allows"): sort the questions by `x` and insert the marks in value order, or store a sorted list in every tree node (a **merge sort tree**). Pick one.
2. With the offline sweep: when you answer the question with threshold `x`, which marks must already be in the Fenwick tree, and which must not?
3. Ties: a mark equal to `x` must **not** be counted.
