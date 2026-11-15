# Fix the at-most-k-distinct window

`starter.py` reads a string `s` and a number `k`, and prints two lines:

1. the length of the **longest** substring of `s` that has **at most `k` distinct characters**;
2. the **number** of substrings of `s` (counted by position, so `"aa"` has three: `a`, `a`, `aa`) that have at most
   `k` distinct characters.

It uses the standard variable sliding window with a dictionary of counts, and it is almost right. It has
**three bugs**. Find them, explain to yourself why each one is wrong, and fix them. Do not rewrite from scratch:
each fix is one or two lines.

Where to look, without saying what is wrong:

1. How many characters are in `s[left..right]`?
2. When a count drops to 0, is that character still "in" the window as far as `len(count)` is concerned?
3. After one character leaves, is the window always good again?

One of the bugs is sneaky: line 1 of the output is right even with it, by luck. Line 2 is what exposes it.

## Input

- Line 1: the string `s` (lower-case letters, at least one).
- Line 2: `k`.

## Output

Two lines: the longest length, then the count.

## Example

Input:

```
eceba
2
```

Output:

```
3
10
```

The longest good substring is `ece`. Good substrings ending at each position: `e` (1); `c`, `ec` (2);
`e`, `ce`, `ece` (3); `b`, `eb` (2); `a`, `ba` (2). That is `1 + 2 + 3 + 2 + 2 = 10`.

## Constraints

- `1 <= len(s) <= 200000`
- `0 <= k <= 26` (with `k = 0` no substring is good: print `0` and `0`)

Use `input()` without a prompt message.
