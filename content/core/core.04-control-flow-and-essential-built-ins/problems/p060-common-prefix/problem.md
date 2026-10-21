# Longest common prefix

Read a line of words. Print the longest **prefix** (starting part) that every word shares, and
its length:

```
Prefix: <prefix>
Length: <n>
```

Comparison is case-sensitive. If the words share nothing, print `Prefix: (none)` and
`Length: 0`. If there are no words, print only `No words`.

**Examples**

| Input | Prefix | Length |
|---|---|---|
| `flower flow flight` | `fl` | 2 |
| `interview internet interval` | `inter` | 5 |
| `dog car` | `(none)` | 0 |
| `same same` | `same` | 4 |
| `solo` | `solo` | 4 |

Try to use `min(..., key=len)`, `all()` and a loop `else`: they fit this problem exactly.
