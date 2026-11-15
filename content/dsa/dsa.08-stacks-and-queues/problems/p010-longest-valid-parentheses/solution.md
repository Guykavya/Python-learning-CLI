## Approach

The stack holds the indices of unmatched `(` above a "wall": the index just before the current valid run (`-1` at first, later an unmatched `)`). When a `)` pops its opener and the stack is not empty, everything between the new top and `i` is balanced, so a run of length `i - stack[-1]` ends at `i`. Record its start as well as its length.

## Code

```python
def longest_valid(s):
    stack = [-1]                     # wall: index just before the current run
    best_start, best_len = 0, 0
    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)      # an unmatched ")": the new wall
            else:
                length = i - stack[-1]
                if length > best_len:            # strictly longer: keep the earliest on ties
                    best_start, best_len = stack[-1] + 1, length
    return s[best_start:best_start + best_len]
```

## Complexity

`O(n)` time: each index is pushed once and popped at most once. `O(n)` memory for the stack.

## Another way

Two counter passes, no stack: scan left to right counting `open` and `close`; when they are equal you have a valid run of length `2 * close`; when `close > open`, reset both. Then scan right to left with the roles swapped (this catches runs like `"(()"` that the first pass misses). It uses `O(1)` memory, but recovering the start index of the run needs a little care on the second pass.
