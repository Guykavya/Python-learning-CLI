## Approach

Chapter section 11. If the longest palindromic prefix of `s` has length `k`, the answer is `reverse(s[k:]) + s`: the added characters mirror the tail around that palindrome, and no shorter addition works (a shorter one would make a longer palindromic prefix).

A prefix `s[:k]` is a palindrome exactly when it equals the suffix of length `k` of `reversed(s)`. So `k` is the longest border of `s + sep + reversed(s)`, as long as **no border can cross the separator**.

**The separator.** With `#` and `s = "#a"` the combined string is `#a#a#`, whose longest border is `#a#` (length 3), longer than `s` itself: it crossed the separator, and the chapter's code returns `"#a"`, which is not a palindrome. No character is safe for every input, but a list can hold `None`, which equals no character. The prefix function uses only indexing and `==`, so it runs on the list unchanged.

```python
def prefix_function(seq):
    pi = [0] * len(seq)
    k = 0
    for i in range(1, len(seq)):
        while k > 0 and seq[i] != seq[k]:
            k = pi[k - 1]
        if seq[i] == seq[k]:
            k += 1
        pi[i] = k
    return pi


def shortest_palindrome(s):
    if not s:
        return s
    seq = list(s) + [None] + list(reversed(s))   # None equals no character: a safe separator
    k = prefix_function(seq)[-1]                 # length of the longest palindromic prefix
    return s[k:][::-1] + s
```

`aacecaaa`: the longest palindromic prefix is `aacecaa` (7), the tail is `a`, so one `a` goes in front.

## Complexity

`O(n)` time and memory (the list has `2n + 1` entries).

## Another way

Pick a separator character that does not occur in `s`: for example the smallest code point not in `set(s)`, found with `next(chr(c) for c in range(0x110000) if chr(c) not in chars)`. Or skip the separator: compute the prefix function of `s` only, then run the KMP scan of `reversed(s)` against `s` (as a pattern), and the final state `k` is the longest prefix of `s` that ends the reversed string. No combined sequence is needed.
