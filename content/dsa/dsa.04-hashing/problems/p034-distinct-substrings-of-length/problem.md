# Distinct substrings of one length

Given a string `s` and a length `L`, count the **distinct** substrings of length exactly `L`.

Putting every slice `s[i:i+L]` into a set works but each slice costs `O(L)` to build and hash, so the program is `O(n * L)`
in time **and memory**. With a **rolling hash**, each window's hash is updated in `O(1)` and the set holds one small integer per
window. Use a large modulus so that two different windows almost never share a hash:

```
B = 911382323          M = 2^61 - 1 = 2305843009213693951
H(window) = sum of v(c_j) * B^(L-1-j)  mod M      with v('a') = 1, ..., v('z') = 26
```

## Input

- Line 1: `s` (lower-case letters).
- Line 2: `L`.

## Output

One integer.

## Example

Input:

```
abcabcab
3
```

Output:

```
3
```

The windows are `abc, bca, cab, abc, bca, cab`: only three different ones.

## Constraints

- `1 <= L <= len(s) <= 200000`
