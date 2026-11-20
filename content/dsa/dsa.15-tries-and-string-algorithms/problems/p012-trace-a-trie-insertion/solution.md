## Approach

Walk each word, create missing nodes, and keep the two counters on every node you step into. Then read the counters of four prefixes.

## Expected output

```text
insert tea: new 3, nodes 4
insert ten: new 1, nodes 5
insert te: new 0, nodes 5
insert tea: new 0, nodes 5
t 4 0
te 4 1
tea 2 2
ten 1 1
```

## Why

| word | nodes walked | new nodes | nodes in total |
|---|---|---|---|
| `tea` | `t`, `te`, `tea` | 3 | 4 |
| `ten` | `t`, `te`, `ten` | 1 (`ten`) | 5 |
| `te` | `t`, `te` | 0 | 5 |
| `tea` | `t`, `te`, `tea` | 0 | 5 |

Counts: every word passes `t` and `te` (4 each). `tea` is passed by the two copies of `tea` and is their end (2, 2). `ten` is passed and ended by `ten` once (1, 1). `te` is the end of one word (`te`), and `t` ends no word.

**After you answer.**

1. The nodes `t` and `te` already exist (made by `tea`). Inserting `te` only adds to pass counts and sets the end count of `te` to 1.
2. `ten` and `te` pass through `te` but not through `tea`: `4 - 2 = 2`.
3. `count_prefix("t")` is the pass count of the node `t`: 4.

## Another way

Count the distinct prefixes instead of drawing: `t`, `te`, `tea`, `ten` are 4 distinct non-empty prefixes, plus the root: 5 nodes. The pass count of a prefix is the number of inserted words (with repeats) that start with it.
