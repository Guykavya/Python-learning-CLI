## Approach

Backtracking over the end of the next piece. The palindrome test is the prune: a non-palindromic piece is never added, so every complete path is a valid partition and nothing must be checked at the end.

## Code

```python
def palindrome_partitions(s):
    result, path = [], []

    def go(start):
        if start == len(s):
            result.append(path[:])
            return
        for end in range(start + 1, len(s) + 1):
            piece = s[start:end]
            if piece == piece[::-1]:
                path.append(piece)
                go(end)
                path.pop()

    go(0)
    return result
```

## Complexity

At most `2^(n-1)` partitions (all letters equal), each copied in `O(n)`; each palindrome test is `O(n)`. Depth `n`.

## Another way

Precompute a table `is_pal[i][j]` with dynamic programming (`s[i] == s[j]` and `is_pal[i+1][j-1]`), so each test in the search is `O(1)`.
