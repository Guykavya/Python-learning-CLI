## Hint 1

`f(i)` = `True` if the first `i` characters `s[:i]` can be cut into words. It is `True` when there is a cut `j < i` such that `s[:j]` can be cut (`f(j)`) and the last piece `s[j:i]` is a word. What is `f(0)`?

## Hint 2

Turn `words` into a `set` first: `in` on a set is `O(1)` on average, on a list it scans every word. The last piece is never longer than the longest word, so `j` only needs to go back that far.

## Hint 3

```
words = set(words); longest = max length of a word
f = [False] * (n + 1); f[0] = True
for i in 1..n:
    for j in max(0, i - longest) .. i - 1:
        if f[j] and s[j:i] in words:
            f[i] = True; break
return f[n]
```
