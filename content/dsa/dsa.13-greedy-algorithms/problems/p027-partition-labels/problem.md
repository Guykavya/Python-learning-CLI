# Partition labels

Cut the string `s` into as **many** pieces as possible, so that every letter appears in **at most one** piece. Write `partition_labels(s)` that returns the **lengths** of the pieces, from left to right.

This problem is **not** worked in the chapter. The hints teach the idea: the last occurrence of each letter.

## Example

```python
>>> partition_labels("ababcbacadefegdehijhklij")
[9, 7, 8]
>>> partition_labels("eccbbbbdec")
[10]
>>> partition_labels("abc")
[1, 1, 1]
>>> partition_labels("")
[]
```

In the first example the pieces are `"ababcbaca"`, `"defegde"` and `"hijhklij"`. Every `a`, `b` and `c` is in the first piece, and so on. A cut after `"ababcbac"` would be wrong: the last `a` is one letter later.

## Constraints

- `0 <= len(s) <= 10**5`, only lowercase letters `a`-`z`.

## Think about

The first piece must contain the first letter `s[0]`, so it reaches at least to the **last** `s[0]`. What else does it then have to reach?
