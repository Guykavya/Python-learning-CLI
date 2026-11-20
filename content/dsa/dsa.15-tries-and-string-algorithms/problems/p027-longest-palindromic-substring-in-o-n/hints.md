## Hint 1

In `t = "#" + "".join(ch + "#" for ch in s)       # length 2n + 1, also for s = ""`, the character `s[j]` sits at index `2j + 1`. A palindrome of length `p[i]` centred at `i` starts at `(i - p[i]) // 2` in `s`.

## Hint 2

The substring `s[l:r]` covers `t` from index `2l + 1` to `2r - 1`, so its centre is `l + r`. It is a palindrome exactly when the longest palindrome there has length `>= r - l`: `p[l + r] >= r - l` (a palindrome centred there stays a palindrome when you cut equal amounts from both ends).

## Hint 3

For the longest one, scan `i` from left to right and update only on a **strictly** larger `p[i]`. Two palindromes of the same length centred at `i1 < i2` start at `(i1 - L) // 2 <= (i2 - L) // 2`, so the first one found starts first.
