# Longest substring without repeats

Find the longest **substring** (a run of neighbouring characters) of `s` in which no character appears twice.

Print its length, and on the next line the substring itself. If several substrings have the maximum length,
print the one that **starts first** (smallest start index).

## Input

One line: the string `s`. It contains only printable characters with no spaces (letters, digits, and signs
such as `!`, `#`, `?`).

## Output

- Line 1: the maximum length.
- Line 2: the earliest substring of that length with no repeated character.

## Example

Input:

```
pwwkew
```

Output:

```
3
wke
```

`pw` has length 2; `wke` and `kew` both have length 3 and no repeats, and `wke` starts first. `pwke` is not a
substring: its letters are not next to each other in `s`.

## Constraints

- `1 <= len(s) <= 200000`

Checking every substring is O(n^2) substrings: far too slow. Use `input()` without a prompt message.
