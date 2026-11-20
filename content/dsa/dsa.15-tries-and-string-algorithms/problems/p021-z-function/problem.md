# Z-function

Write `z_function(s)` that returns the list `z` of chapter section 12: `z[i]` is the length of the longest common prefix of `s` and `s[i:]`, with the convention `z[0] = len(s)`. It must run in `O(n)` using the **Z-box**.

## Example

```python
>>> z_function("aabxaab")
[7, 1, 0, 0, 3, 1, 0]
>>> z_function("abacaba")
[7, 0, 1, 0, 3, 0, 1]
>>> z_function("aaaa")
[4, 3, 2, 1]
>>> z_function("")
[]
```

## Constraints

- `0 <= len(s) <= 5 * 10**5`; any characters.
- The tests compare with the definition on random strings over `"ab"`, then time strings of 5 * 10**5 characters, where comparing from scratch at every `i` is `O(n**2)`.

## Think about

1. The Z-box `[l, r)` says `s[l:r] == s[0:r - l]`. If `i` is inside it, which earlier value tells you something about `z[i]`, and why can you trust it only up to `r`?
2. Why does `r` never move left, and why does that make the total work `O(n)`?
3. When does the box move?
