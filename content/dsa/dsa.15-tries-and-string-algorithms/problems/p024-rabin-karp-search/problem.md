# Rabin-Karp search

Write the Rabin-Karp search of chapter section 13 with **several** hash functions at once. A hash function is a pair `(B, M)`; the hash of a string `w` is

```text
hash(w) = (ord(w[0]) * B**(m-1) + ord(w[1]) * B**(m-2) + ... + ord(w[m-1])) % M
```

1. `window_hashes(text, m, B, M)`: the list of the hashes of all windows `text[i:i + m]`, for `i = 0 .. len(text) - m`, computed with the **rolling** update (each window in `O(1)` after the first).
2. `rabin_karp(text, pattern, params=((131, 1_000_000_007), (137, 998_244_353)), verify=True)`: the sorted start positions where the window's hash equals the pattern's hash **for every pair in `params`**. If `verify` is true, also compare the strings and keep only real matches. The empty pattern gives `list(range(len(text) + 1))`.

## Example

```python
>>> window_hashes("abcabcab", 3, 31, 101)           # equal windows, equal hashes
[0, 81, 72, 0, 81, 72]
>>> rabin_karp("abababab", "abab")
[0, 2, 4]
>>> text = "xxdiexcabx"                                # 'die' and 'cab' collide for (31, 101)
>>> rabin_karp(text, "cab", params=((31, 101),), verify=False)
[2, 6]
>>> rabin_karp(text, "cab", params=((31, 101),), verify=True)
[6]
>>> rabin_karp(text, "cab", params=((31, 101), (37, 103)), verify=False)
[6]
```

The last three lines are the point of the problem: a single small modulus gives a false alarm at position 2; verification or a second hash removes it.

## Constraints

- Texts up to 10**6 characters; any characters. `window_hashes` returns `[]` when `m > len(text)`; `m >= 1` there.
- Expected `O(n + m)` per hash pair.

## Think about

1. How does the hash of `text[i + 1:i + m + 1]` follow from the hash of `text[i:i + m]`? Which power of `B` do you need, and how do you compute it once?
2. In Python, can the subtraction in the rolling update leave a negative number after `% M`?
3. Why does the second pair remove the false alarm, and why can it not remove a real match?
