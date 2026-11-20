# Prefix function

Write `prefix_function(s)` that returns the list `pi` of chapter section 10: `pi[i]` is the length of the longest **proper** prefix of `s[:i + 1]` that is also a suffix of it (its longest border). It must run in `O(n)`.

## Example

```python
>>> prefix_function("abcabcd")
[0, 0, 0, 1, 2, 3, 0]
>>> prefix_function("aabaaab")
[0, 1, 0, 1, 2, 2, 3]
>>> prefix_function("aaaa")
[0, 1, 2, 3]
>>> prefix_function("")
[]
```

## Constraints

- `0 <= len(s) <= 5 * 10**5`, any characters.
- The tests compare your list with the definition on thousands of random strings over `"ab"` (many partial matches), then time strings of 5 * 10**5 characters.

## Think about

1. If `pi[i - 1] = k`, which single letter decides whether the border grows to `k + 1`?
2. If it does not grow, why is `pi[k - 1]` the next length to try, and not `k - 1`?
3. The fallback loop is inside a `for` loop. Why is the total work still `O(n)`?
