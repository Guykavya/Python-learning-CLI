# Count distinct substrings

Write `count_distinct(s)` that returns how many **different non-empty** substrings `s` has. (The chapter mentions this as a classic use of the Z-function in section 12, "Uses of the Z-function", and leaves it as practice.)

## Example

```python
>>> count_distinct("aba")        # a, b, ab, ba, aba
5
>>> count_distinct("aaa")        # a, aa, aaa
3
>>> count_distinct("abc")        # every substring is different: 3 + 2 + 1
6
>>> count_distinct("")
0
```

## Constraints

- `0 <= len(s) <= 2000`; any characters.
- A string of length 2000 has about 2 million substrings with about 1.3 * 10**9 characters in total: a `set` of all of them does not fit in memory. Aim for `O(n**2)` time and `O(n)` extra memory.

## Think about

1. Build `s` one character at a time. When you append a character `c` to `t`, which new substrings appear? (They all end with the new `c`.)
2. Which of those suffixes of `t + c` are **really** new? Why is it enough to know the longest suffix of `t + c` that already occurred earlier?
3. Reverse `t + c`. How does the Z-function of the reversed string find that longest earlier occurrence?
