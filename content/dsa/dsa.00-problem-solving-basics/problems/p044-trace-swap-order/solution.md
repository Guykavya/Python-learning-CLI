## Walkthrough

**Loop 1** (`a, b = b, a + b`). The right side is computed from the old values, then both are stored.

| `step` | old `a`, `b` | right side `b`, `a + b` | new `a`, `b` | printed |
|---|---|---|---|---|
| 0 | 0, 1 | 1, 1 | 1, 1 | `together 1 1` |
| 1 | 1, 1 | 1, 2 | 1, 2 | `together 1 2` |
| 2 | 1, 2 | 2, 3 | 2, 3 | `together 2 3` |
| 3 | 2, 3 | 3, 5 | 3, 5 | `together 3 5` |
| 4 | 3, 5 | 5, 8 | 5, 8 | `together 5 8` |

**Loop 2** (`a = b`, then `b = a + b`). The second line sees the **new** `a`.

| `step` | old `a`, `b` | after `a = b` | after `b = a + b` | printed |
|---|---|---|---|---|
| 0 | 0, 1 | `a` = 1 | `b` = 1 + 1 = 2 | `one by one 1 2` |
| 1 | 1, 2 | `a` = 2 | `b` = 2 + 2 = 4 | `one by one 2 4` |
| 2 | 2, 4 | `a` = 4 | `b` = 4 + 4 = 8 | `one by one 4 8` |
| 3 | 4, 8 | `a` = 8 | `b` = 8 + 8 = 16 | `one by one 8 16` |
| 4 | 8, 16 | `a` = 16 | `b` = 16 + 16 = 32 | `one by one 16 32` |

Full output:

```
together 1 1
together 1 2
together 2 3
together 3 5
together 5 8
one by one 1 2
one by one 2 4
one by one 4 8
one by one 8 16
one by one 16 32
```

## Key idea

- Tuple assignment `a, b = b, a + b` evaluates the whole right side first, then assigns. Both new values come from
  the old pair. This is what Fibonacci needs.
- Two separate lines run in order. After `a = b` the old `a` is lost, and `b = a + b` becomes `b = 2 * b`.
  So the second loop gives powers of 2, not Fibonacci numbers.
- Without tuple assignment you need a temporary variable: `old_a = a`, `a = b`, `b = old_a + b`.
- Whenever an update uses a value you are about to overwrite, ask: "does this line need the old value or the new one?"
