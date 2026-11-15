# Minimum window substring

Given strings `s` and `t`, find the **shortest** substring of `s` that contains every character of `t`, **with
multiplicity**: if `t` has two `a`s, the window needs at least two `a`s. Other characters may be in the window too.

Rules that pin the answer:

- Characters are case-sensitive: `A` and `a` are different.
- If several shortest windows exist, print the one that **starts earliest**.
- If no window exists, print `-1`.

This is the variable sliding window in its "shortest" form: grow `right` until the window is good, then shrink
`left` while it stays good, and record the window just before it breaks.

## Input

- Line 1: `s`.
- Line 2: `t`.

## Output

One line: the window, or `-1`.

## Example

Input:

```
ADOBECODEBANC
ABC
```

Output:

```
BANC
```

More examples:

| s | t | output | why |
|---|---|---|---|
| `baXab` | `ab` | `ba` | `ba` and `ab` are both shortest; `ba` starts first |
| `abca` | `aa` | `abca` | two `a`s are needed |
| `abc` | `d` | `-1` | no `d` at all |
| `a` | `aa` | `-1` | not enough `a`s |

## Constraints

- `1 <= len(s), len(t) <= 200000`
- Both strings contain only the letters `a`-`z` and `A`-`Z`.

Use `input()` without a prompt message.
