# All orderings

1. Write `permutations(items)` that returns a list of **all orderings** of the list `items`, each
   as a list, in this order: first all orderings that start with `items[0]`, then those that
   start with `items[1]`, and so on, applying the same rule recursively to the rest.
   Treat the items as distinct by position (so `[1, 1]` gives two orderings).
2. Write `anagrams(word)` that returns a **sorted** list of the **different** strings that can be
   made by rearranging all the letters of `word`. Use `permutations`.

Recursive, no `itertools`, and `items` must not change.

**Examples**

```python
permutations([1, 2, 3])
# [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
permutations([])          # [[]]
permutations(["x"])       # [['x']]
anagrams("abc")           # ['abc', 'acb', 'bac', 'bca', 'cab', 'cba']
anagrams("aab")           # ['aab', 'aba', 'baa']
```
