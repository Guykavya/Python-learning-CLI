## Walkthrough

| Line | Output | Why |
|---|---|---|
| `print(b)` | `None` | `append` changes `a` and returns `None` |
| `print(a)` | `[3, 1, 2, 5]` | the append did happen |
| `print(a.pop(), a)` | `5 [3, 1, 2]` | `pop` returns the item it removed |
| `print(sorted(a), a)` | `[1, 2, 3] [3, 1, 2]` | `sorted` makes a new list; `a` is unchanged |
| `print(c, a)` | `None [1, 2, 3]` | `sort` sorted `a` in place and returned `None` |
| `print(a.extend([4]))` | `None` | `extend` returns `None` |
| `print(len(a), a.index(4))` | `4 3` | `a` is `[1, 2, 3, 4]` |
| `print(a)` | `None` | `a = a.reverse()` reversed the list, then bound `a` to `None` |
