# Valid anagram

Two strings are **anagrams** if one is a rearrangement of the other: they use exactly the same characters, the same
number of times. Read two strings and print `YES` if they are anagrams, otherwise `NO`. Case matters (`a` and `A` are
different characters).

## Input

- Line 1: `s`.
- Line 2: `t`.

## Output

`YES` or `NO`.

## Example

Input:

```
listen
silent
```

Output:

```
YES
```

`rat` and `car` give `NO`: same length, but `t` and `c` do not match. `aab` and `abb` give `NO` too: the letters
match but the **counts** do not.

## Constraints

- `1 <= len(s), len(t) <= 200000`
- Any visible characters, no spaces.
