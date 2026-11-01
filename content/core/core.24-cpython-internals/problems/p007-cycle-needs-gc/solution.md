## Approach

Keep reference counting and the cycle collector apart. Reference counting acts immediately and
only sees counts. The collector acts only when it runs (here only at `gc.collect()`) and finds
groups of objects that are referenced only from inside the group.

| Code | Reasoning | Output |
|---|---|---|
| first print | both nodes alive; `rb()` is B, and B's partner is A | `True b a` |
| after `del a` | the name is gone, but `B.partner` still refers to A | `after del a: False` |
| after `del b` | each node is referenced by the other, so both counts are 1, not 0 | `after del b: False False` |
| `gc.collect()` | the collector finds the unreachable pair and frees both; each death calls `gone` | `freed`, `freed` |
| `found > 0` | `gc.collect()` returns how many unreachable objects it found; the exact number varies by version, but it is at least 2 | `collected: True` |
| after collect | both weak references are now dead | `after collect: True True` |
| `del c` | no cycle: the count drops to 0 and C is freed at once, before the next line | `freed`, `no cycle: True` |

## Full output

```
True b a
after del a: False
after del b: False False
freed
freed
collected: True
after collect: True True
freed
no cycle: True
```

## Complexity

Reference counting costs O(1) per change. A full collection walks every object the collector
tracks, which is why it runs only occasionally and why cycles can sit in memory for a while.

## Another way

Break the cycle yourself before dropping the names (`a.partner = None`), and both nodes die
at `del` time with no collector needed. Or make the back link weak:
`self.partner = weakref.ref(other)`. Parent/child trees often keep a strong reference from
parent to child and a weak one back up, so no cycle is ever formed.
