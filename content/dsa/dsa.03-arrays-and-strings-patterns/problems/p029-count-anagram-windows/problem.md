# Count anagram windows

Two strings are **anagrams** when they contain the same letters the same number of times, in any order
(`bac` and `abc`). Count the positions `i` where the substring of `text` that starts at `i` and has the same
length as `pattern` is an anagram of `pattern`. Overlapping windows count separately.

## Input

- Line 1: `text`.
- Line 2: `pattern`.

Both contain only lowercase letters `a` to `z`.

## Output

One line: the number of anagram windows. If `pattern` is longer than `text`, the answer is `0`.

## Example

Input:

```
cbaebabacd
abc
```

Output:

```
2
```

The windows of length 3 are `cba`, `bae`, `aeb`, `eba`, `bab`, `aba`, `bac`, `acd`. Only `cba` (start 0) and `bac`
(start 6) use exactly one `a`, one `b` and one `c`.

## Constraints

- `1 <= len(text), len(pattern) <= 200000`

Sorting or counting each window from scratch costs O(m) per window: too slow when both strings are long.
Use `input()` without a prompt message.
