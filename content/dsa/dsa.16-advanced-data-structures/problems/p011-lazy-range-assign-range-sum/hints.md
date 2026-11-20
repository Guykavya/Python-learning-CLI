## Hint 1

The tag is "every element below me still has to become `v`". Applying it to a node **replaces** its sum: `s = v * (hi - lo)`, and replaces any older tag: the newer assignment wins (chapter section 9).

## Hint 2

Use `None` for "no tag" and test it with `is not None`. With `0` as the marker (or `if tag:`), an assignment of 0 is silently forgotten when it should be pushed.

## Hint 3

```
_apply(node, lo, hi, v): s[node] = v * (hi - lo); tag[node] = v
_push(node, lo, hi):
    if tag[node] is not None: apply it to both children; tag[node] = None
```

The rest (cover with whole nodes, push before descending, recompute after) is the same as p010.
