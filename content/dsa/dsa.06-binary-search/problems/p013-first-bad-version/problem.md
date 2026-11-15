# First bad version (interactive)

Versions `1, 2, ..., n` of a program were released. From some version `B` on, every version is bad (`B` and all later ones). You can ask the test program whether a version is bad. Find `B` with as few questions as possible.

This is an **interactive** problem: your program talks to the test program through the keyboard and the screen.

- First the test sends one line: `n`.
- To ask about version `v`, print `? v` and **flush** (`print("? 5", flush=True)`). The reply is one line: `1` if `v` is bad, `0` if good.
- When you know `B`, print `! B` (also with `flush=True`) and stop.

You may ask at most `bit_length(n) + 1` questions (that is `floor(log2 n) + 2`). Asking about every version one by one will fail for big `n`.

## Constraints

- `1 <= n <= 10^18`, `1 <= B <= n`

## Example

Your program sees `n = 5`. A talk where `B = 4` can look like this (lines you print start with `?` or `!`):

```
5          <- sent by the test
? 3        <- you print
0          <- reply: version 3 is good
? 4        <- you print
1          <- reply: version 4 is bad
! 4        <- you print
```

(Two questions are enough here because the version before 4 is known good from the first reply.)
