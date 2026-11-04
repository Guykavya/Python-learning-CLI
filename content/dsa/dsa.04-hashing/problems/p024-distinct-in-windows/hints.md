## Hint 1

When the window moves one step to the right, how many elements enter and how many leave? Can you update a table instead of rebuilding it?

## Hint 2

Keep `count[v]` for the values currently in the window. Entering `v`: `count[v] += 1`. Leaving `v`: `count[v] -= 1` and, at 0, `del count[v]`.

## Hint 3

```
build count for a[:k]; answer = [len(count)]
for i in range(k, n):
    add a[i]
    remove a[i-k] (delete the key at 0)
    answer.append(len(count))
```
