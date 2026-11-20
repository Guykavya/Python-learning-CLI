## Hint 1

If `s[:k]` is a palindrome, then `reverse(s[k:]) + s` is a palindrome: the added part mirrors the tail. The longer the palindromic prefix, the less you add, so you need the **longest** palindromic prefix.

## Hint 2

A prefix `s[:k]` is a palindrome exactly when it equals the last `k` characters of `reversed(s)`. So it is a border of `s + sep + reversed(s)`, and the separator stops borders from being longer than `s`. The prefix function's last value is the answer `k`.

## Hint 3

Use lists: `seq = list(s) + [None] + list(reversed(s))`. `None` is never equal to a character, so no border can cross it. The prefix function only uses `==` / `!=` and indexing, so it works on this list unchanged. Then `k = pi[-1]` and the answer is `s[k:][::-1] + s`.
