# Decode ways

A message of letters was encoded as digits with `A -> 1`, `B -> 2`, ..., `Z -> 26`, and the digits were written together without separators. Write `decode_ways(s)` that returns the number of ways to decode the digit string `s` back into letters (chapter section 5).

A piece is one digit `1`-`9`, or two digits `10`-`26`. A piece may **not** start with `0`: `"06"` is not `F`.

## Example

```python
>>> decode_ways("226")        # 2 2 6 (BBF), 22 6 (VF), 2 26 (BZ)
3
>>> decode_ways("12")         # 1 2 (AB), 12 (L)
2
>>> decode_ways("06")         # no letter is "0" and "06" is not allowed
0
>>> decode_ways("10")         # only J
1
>>> decode_ways("2101")       # 2 10 1 is the only one
1
```

## Constraints

- `1 <= len(s) <= 5000`, `s` contains only digits. Return the exact count (up to about 1000 digits).
- `O(n)`. Without a memo, the recursion is exponential (`"1" * 60` never finishes); with a memo it is 5000 calls deep, too deep for Python. Fill a table.

## Think about

What are the two choices for the **last** piece of the first `i` characters? When is each one allowed? Why is `f(0) = 1`, the number of ways to decode the empty string?
