# Manacher's algorithm

Write Manacher's algorithm (chapter section 15):

- `manacher(s)`: the list `p` of length `2 * len(s) + 1`. Insert a separator between all characters and at both ends (`"aba"` becomes `#a#b#a#`); `p[i]` is the largest radius `k` such that the transformed string reads the same `k` steps to the left and right of `i`. Then `p[i]` is also the **length** of the longest palindrome of `s` centred there.
- `count_palindromes(s)`: the number of palindromic substrings of `s`, counted by position (`aaa` has 6: three `a`, two `aa`, one `aaa`).

`s` may contain **any** characters, including `#`.

## Example

```python
>>> manacher("babad")
[0, 1, 0, 3, 0, 3, 0, 1, 0, 1, 0]
>>> manacher("")
[0]
>>> count_palindromes("aaa"), count_palindromes("abba"), count_palindromes("abc")
(6, 6, 3)
>>> manacher("#a#")                 # '#' inside s is harmless: see "Think about"
[0, 1, 0, 3, 0, 1, 0]
```

## Constraints

- `0 <= len(s) <= 2 * 10**5`; any characters.
- `O(n)`. Expanding around every centre is `O(n**2)` on `aaaa...`: the tests use 2 * 10**5 equal letters.

## Think about

1. For a centre `i` inside the rightmost palindrome `(c, r)`, why does the mirror position `2c - i` give a starting radius, and why must it be capped at `r - i`?
2. Why is the whole algorithm `O(n)` although it has a `while` loop inside a `for` loop?
3. When the algorithm compares `t[i - k]` with `t[i + k]`, are those both separators, or both characters of `s`? Why does that make a `#` inside `s` harmless (unlike the separator of p020)?
4. How many palindromes are centred at `i` if `p[i] = 5`? If `p[i] = 4`?
