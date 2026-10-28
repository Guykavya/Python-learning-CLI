## Approach

Track two namespaces.

| Line | `main.level` | `settings.level` | note |
|---|---|---|---|
| from-import | 1 | 1 | both names point to `1` |
| `bump()` | 1 | 2 | `global` in `bump` means `settings` |
| `settings.level = 10` | 1 | 10 | rebinds the name in `settings` |
| `level = 99` | 99 | 10 | rebinds the name in `main` |

The list is different: `names.append("ben")` changes the **one** list object, so `settings.names` shows
`['ann', 'ben']`. Then `settings.names = ["cat"]` rebinds only the name in `settings`; `main.names` still
points to the old list.

`from settings import level` again copies the current `settings.level`, which is 10. The last line calls
`bump()` first (it returns 11), then reads `main.level`, which is still 10.

## Output

```text
1 1
1 2
1 10
99 10
['ann', 'ben']
['ann', 'ben'] ['cat']
10
11 10
```

## Complexity

O(1).

## Another way

When you want to see live changes, use `import settings` and write `settings.level`. That looks up the
name in the module each time, instead of keeping your own copy of the binding.
