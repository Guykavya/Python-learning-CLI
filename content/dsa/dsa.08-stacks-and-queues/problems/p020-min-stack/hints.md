## Hint 1

When you push `x`, you can compute "the minimum of the stack including `x`" in `O(1)` from the minimum just before it. If you store that number next to `x`, what will be on top after a `pop`?

## Hint 2

Store pairs `(value, min_so_far)`:

```
push(x): m = x if empty else min(x, items[-1][1]); items.append((x, m))
pop():   return items.pop()[0]
top():   return items[-1][0]
get_min(): return items[-1][1]
```

An empty list already raises `IndexError` for `pop()` and `[-1]`.
