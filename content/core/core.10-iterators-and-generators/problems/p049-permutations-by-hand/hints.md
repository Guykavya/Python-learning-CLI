## Hint 1

What is the smallest case? When `r` is 0, there is exactly one arrangement: the empty tuple. For a
bigger `r`: which item can come first? Every position in turn. What do you need after it?

## Hint 2

Put the items in a list `pool` once. For each index `i`: `first = pool[i]`,
`rest = pool[:i] + pool[i+1:]`. Every arrangement of `r - 1` items from `rest`, with `first` put in
front, is an answer. Loop over a **recursive generator call**, do not turn it into a list.

A helper `_perms(pool, r)` keeps the recursion simple; `perms` only prepares `pool` and `r`.

## Hint 3

```
_perms(pool, r):
    if r == 0: yield (); return
    for i in range(len(pool)):
        rest = pool without position i
        for tail in _perms(rest, r - 1):
            yield (pool[i],) + tail

anagrams(word):
    seen = set()
    for t in perms(word):
        s = "".join(t)
        if s not in seen: seen.add(s); yield s
```
