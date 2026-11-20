# Smallest period of a string

A sensor sends a signal as a string of letters, and you want to know how often it repeats. A string `s` of length `n` has **period** `p` (for `1 <= p <= n`) if `s[i] == s[i + p]` for every `i` with `i + p < n`. Every string has the period `n`. Write two functions (chapter section 11, "Borders, periods and repeated blocks"):

- `smallest_period(s)`: the smallest period of `s`;
- `all_periods(s)`: every period of `s`, in increasing order.

`s` is not empty. The last block may be cut short: `abcab` has period 3 (`abc` + `ab`).

## Example

```python
>>> smallest_period("abcabcab"), all_periods("abcabcab")
(3, [3, 6, 8])
>>> smallest_period("abcab"), smallest_period("aaaa"), smallest_period("abcd")
(3, 1, 4)
>>> all_periods("aabaa")
[3, 4, 5]
```

## Constraints

- `1 <= len(s) <= 5 * 10**5`; any characters.
- `O(n)`: checking every `p` with a loop over the string is `O(n**2)`.

## Think about

1. If `s` has a border of length `b`, why does it have the period `n - b`? And the other way round?
2. How do you list **all** borders using the prefix function, not only the longest?
3. Why is `all_periods("aabaa")` not `[3]` plus the multiples of 3?
