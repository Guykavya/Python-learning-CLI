## Walkthrough

- **A** `box["a"]` and `box["b"]` are one list. `deepcopy` copies it once (for `"a"`), stores it in
  `memo`, and reuses that copy for `"b"`. So `c["a"]` and `c["b"]` are one new list: the append
  through `c["a"]` shows in `c["b"]`: `[0, 1]`.
- **B** The original was never touched: `[0]`.
- **C** Shared with each other inside the copy, not shared with the original: `True False`.
- **D** `grid` holds the same inner list twice; the deep copy holds one *new* inner list twice.
  Writing `g2[0][0]` therefore also shows in `g2[1]`: `[[7, 0], [7, 0]]`. `deepcopy` does **not**
  fix the `* 2` sharing bug; it copies it faithfully.
- **E** The original is unchanged: `[[0, 0], [0, 0]]`.
- **F** `loop` contains itself. `deepcopy` creates the new list, puts it in `memo`, then copies the
  items; the second item is `loop` again, found in `memo`, so the copy contains **itself**:
  `True False`.
- **G** Printing a list that contains itself shows `[...]`: `[1, [...]]`.
- **H** The second call is given the same `memo`, which already maps `id(x)` to `first`, so it
  returns `first` again: `True False`.
- **I** Both slots of the tuple are the same list, so the copy has one new list in both slots,
  and because it contains a list, it is a new tuple: `True False`.
- **J** Copying `a` copies `a.peers`, which copies `b`, whose `peers` contain `a`, already in
  `memo` as `a2`. So the copied `b` points back to `a2`: `b True False`.
- **K** `copy.copy` makes a new outer list holding the very same `shared`: `True`. The deep copy
  meets `shared` at depth 1 and again inside the inner list; both become the same new list:
  `True`, and that list is not the original: `False`.

## The exact output

```text
A [0, 1]
B [0]
C True False
D [[7, 0], [7, 0]]
E [[0, 0], [0, 0]]
F True False
G [1, [...]]
H True False
I True False
J b True False
K True True False
```
