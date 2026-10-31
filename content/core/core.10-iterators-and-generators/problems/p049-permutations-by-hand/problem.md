# Permutations by hand, lazily

`itertools.permutations` is easy to use. Can you build it? Recursion and generators fit together
well here: "all arrangements of `abc`" = `a` + (all arrangements of `bc`), then `b` + (all
arrangements of `ac`), then `c` + (all arrangements of `ab`).

Write in `solution.py`, **without importing itertools**:

## 1. `perms(items, r=None)`

Yield all arrangements of `r` items taken from `items` (all of them if `r` is `None`), as **tuples**,
in **exactly the same order** as `itertools.permutations(items, r)`.

- Items are chosen by **position**, so equal items are not merged: `perms("aa")` gives
  `("a", "a")` twice, like the real one.
- `r = 0` gives one empty tuple `()`. `r` larger than the number of items gives nothing.
- It must be **lazy**: the first arrangement of 9 items must come out at once, without building
  all 362,880 of them. So do not collect results in a list anywhere, also not in the recursive calls.

```python
list(perms("abc", 2))
# [("a", "b"), ("a", "c"), ("b", "a"), ("b", "c"), ("c", "a"), ("c", "b")]
list(perms([1, 2, 3]))
# [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]
```

## 2. `anagrams(word)`

Yield every **different** string you can make from all the letters of `word`, each once, in the
order of `perms`. Use `perms`, `"".join`, and a set.

```python
list(anagrams("aab"))      # ["aab", "aba", "baa"]
```
