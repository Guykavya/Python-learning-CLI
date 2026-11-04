# Trace a variable sliding window

This is the "longest substring without repeats" window. It prints a `drop` line every time a character leaves
the window from the left, and one state line `r s[r] l window best` after each new character. Predict **exactly**
what the program prints. Do not run it.

```python
def longest_unique(s):
    seen = set()
    l = 0
    best = 0
    for r in range(len(s)):
        while s[r] in seen:
            print("drop", s[l])
            seen.remove(s[l])
            l += 1
        seen.add(s[r])
        best = max(best, r - l + 1)
        print(r, s[r], l, s[l:r + 1], best)
    return best


print("answer", longest_unique("pwwkew"))
print("answer", longest_unique("dvdf"))
print("answer", longest_unique("abba"))
```

Write your answer in `answer.txt`, one line per printed line. The lines look like `1 w 0 pw 2` and `drop p`.

## How to work

Keep three things on paper: the set `seen`, the left end `l`, and `best`. For each `r`:

1. Is `s[r]` already in `seen`? If yes, drop `s[l]` (print it), remove it from the set, move `l` right, and ask
   again. Only stop when `s[r]` is no longer inside.
2. Add `s[r]`, compute the window `s[l:r+1]` and its length, and update `best`.

Watch the second `w` in `pwwkew`: which characters must leave before it can enter? And in `dvdf`: does the window
restart from scratch, or keep the `v`?

## After you answer

1. In `pwwkew`, how many `drop` lines in total? Is it ever more than the length of the string? Why does that make
   the whole loop O(n)?
2. A common wrong idea restarts the window at the repeated character (`l = r`). What would it give for `dvdf`?
3. In `abba`, the last `a` is not dropped. Why is the first `a` no longer in `seen` at that moment?
