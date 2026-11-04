# Find every occurrence of a pattern

Find every position where a pattern `p` occurs in a text `t` (overlaps allowed). This is the **Rabin-Karp** idea: compute
the hash of `p` once, then slide a window of length `m = len(p)` over `t` and update its hash in `O(1)` per step. Only
compare the actual characters when the two hashes are equal.

Rolling update for a window `t[i..i+m-1]` (letters `a = 1, ..., z = 26`, `B = 131`, `M = 1_000_000_007`):

```
H_next = ((H - v(t[i]) * B^(m-1)) * B + v(t[i+m])) mod M
```

Use these fixed `B` and `M` if you hash (the tests contain no adversarial strings), and **verify** each hash match with
`t[i:i+m] == p`.

## Input

- Line 1: the text `t`.
- Line 2: the pattern `p`.

## Output

- Line 1: the number of occurrences.
- Line 2: the 0-based starting positions in increasing order, separated by spaces (an empty line when there are none).

## Example

Input:

```
abababa
aba
```

Output:

```
3
0 2 4
```

The occurrences overlap: `aba` starts at 0, at 2 and at 4.

## Constraints

- `1 <= len(p) <= len(t) <= 200000`
- Lower-case letters only.
