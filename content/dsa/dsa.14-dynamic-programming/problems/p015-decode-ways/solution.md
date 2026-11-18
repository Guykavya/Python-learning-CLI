## Approach

The recipe from chapter section 5:

- **State:** `f(i)` = the number of ways to decode the first `i` characters.
- **Transition:** the last piece is one digit `s[i-1]` (valid if not `'0'`), giving `f(i-1)` ways, or two digits `s[i-2:i]` (valid if between 10 and 26), giving `f(i-2)` ways. Add the valid ones.
- **Base:** `f(0) = 1`.
- **Answer:** `f(n)`.

```python
def decode_ways(s):
    n = len(s)
    f = [0] * (n + 1)
    f[0] = 1                                   # the empty prefix: one way (do nothing)
    for i in range(1, n + 1):
        if s[i - 1] != "0":                    # last piece is one digit
            f[i] += f[i - 1]
        if i >= 2 and 10 <= int(s[i - 2:i]) <= 26:   # last piece is two digits
            f[i] += f[i - 2]
    return f[n]
```

The test `10 <= int(...)` rejects `"06"` (value 6) as well as `"00"`. A string with an impossible zero simply gets `f[i] = 0` at that point, and all later cells that depend on it stay 0.

## Complexity

`O(n)` time and `O(n)` space (two rolling variables give `O(1)`).

## Another way

Read from the front with a memo: `g(i)` = the ways to decode `s[i:]`; `g(n) = 1`; `g(i) = 0` if `s[i] == '0'`; else `g(i + 1)`, plus `g(i + 2)` if `s[i:i+2] <= "26"` as a number. That is the brute force of the tests plus a notebook. It is right, but it recurses `n` deep, so for length 5000 fill it as a table from `i = n` down to 0 (the arrows point right, loop backwards).
