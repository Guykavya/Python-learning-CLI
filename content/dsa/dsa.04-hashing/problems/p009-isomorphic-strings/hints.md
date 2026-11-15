## Hint 1

A mapping from `s` to `t` must be a function: one answer per character. Is that enough? Try `ab` and `aa`.

## Hint 2

You need two rules: the same `s` char must always give the same `t` char, **and** no `t` char may come from two different `s` chars. Keep two dictionaries, or a dictionary and a set.

## Hint 3

```
forward = {}; backward = {}
for a, b in zip(s, t):
    if forward.get(a, b) != b or backward.get(b, a) != a: NO
    forward[a] = b; backward[b] = a
YES
```
