## Approach

Choose, explore, un-choose. Each level fixes one position. Because `"0"` is tried before `"1"` at every level, the leaves come out in dictionary order. For `n = 0` the very first call is already complete and records `""`.

## Code

```python
def binary_strings(n):
    result = []
    path = []

    def go():
        if len(path) == n:
            result.append("".join(path))
            return
        for ch in "01":
            path.append(ch)     # choose
            go()                # explore
            path.pop()          # un-choose

    go()
    return result
```

## Complexity

`2^n` strings of length `n`: `O(n * 2^n)` time and output size. Depth `n`.

## Another way

Pass a new string down instead of changing a shared list (no un-choose needed):

```python
def binary_strings(n, prefix=""):
    if len(prefix) == n:
        return [prefix]
    return binary_strings(n, prefix + "0") + binary_strings(n, prefix + "1")
```
