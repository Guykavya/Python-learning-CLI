## Walkthrough

- **A** `shallow["name"] = "B"` rebinds the key in the shallow dict only. `team` (and `deep`) still
  say `"A"`: `A A B A`.
- **B** The members list is shared by `team`, `alias` and `shallow`; the `append` through
  `shallow` shows up in `team`: `['ann', 'bo', 'cy']`.
- **C** `deep` got its own list before the append: `['ann', 'bo']`.
- **D** The meta dict is shared by `team`, `alias` and `shallow`; `alias[...] = 2` changes it for
  all three. `deep` has its own meta dict, set to 9: `2 2 9`.
- **E** The shallow copy's list *is* the original list; the deep copy's is not: `True False`.
- **F** `alias is team` (same object); the shallow copy is a different dict, and since its name
  is now `"B"` it is not even equal: `True False False`.
- **G, H** `rows[:]` is a new outer list with the same two inner lists. `r2[0] = [9, 9]` replaces
  the first slot in `r2` only. `r2[1][0] = 8` writes into the second inner list, which is shared:
  `rows` is `[[1, 2], [8, 4]]`, `r2` is `[[9, 9], [8, 4]]`.
- **I** `[[0] * 2] * 2` puts the **same** inner list in both slots, so writing `grid[0][0]` also
  shows in `grid[1][0]`: `[[5, 0], [5, 0]]`. (Build grids with `[[0] * 2 for _ in range(2)]`.)
- **J** A tuple cannot change, so a shallow copy would be pointless: `copy.copy` returns the same
  tuple: `True`.
- **K** This tuple contains a list. A deep copy must copy the list, so it must also build a new
  tuple to hold it: `False False True` (new tuple, new list, equal contents).
- **L** A tuple of only immutable things needs no copying at all, even for `deepcopy`: `True`.

## The exact output

```text
A A B A
B ['ann', 'bo', 'cy']
C ['ann', 'bo']
D 2 2 9
E True False
F True False False
G [[1, 2], [8, 4]]
H [[9, 9], [8, 4]]
I [[5, 0], [5, 0]]
J True
K False False True
L True
```
