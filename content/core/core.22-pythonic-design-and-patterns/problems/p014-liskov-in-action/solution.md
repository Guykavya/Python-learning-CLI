## Approach

Run `check` once per line. `check` calls `reverse_all`, which pushes every item, then pops until
`len(stack)` is 0.

| Call | What happens | Output |
|---|---|---|
| `plain`, `[1, 2, 3]` | pushes 1,2,3; pops 3,2,1; expected `[3, 2, 1]` | `plain ok [3, 2, 1]` |
| `limit3`, 3 items | pushes at sizes 0,1,2 are below the limit 3 | `limit3 ok [3, 2, 1]` |
| `limit2`, 3 items | third push sees size 2, `2 >= 2`, raises `OverflowError` | `limit2 raised OverflowError` |
| `dedup`, `[1, 2, 3]` | no duplicates | `dedup ok [3, 2, 1]` |
| `dedup-repeat`, `[1, 2, 1]` | second `1` is skipped; pops give `[2, 1]`, expected `[1, 2, 1]` | `dedup-repeat wrong [2, 1]` |
| `counting`, `[4, 5]` | same as a Stack; counter reaches 2 | `counting ok [5, 4]` then `pushes 2` |
| `frozen`, `[1]` | first push raises `TypeError` | `frozen raised TypeError` |
| `frozen-empty`, `[]` | nothing is pushed, nothing popped | `frozen-empty ok []` |
| the loop | all are subclasses; only `Stack` uses the original `push` object | five lines (see below) |

Full output:

```
plain ok [3, 2, 1]
limit3 ok [3, 2, 1]
limit2 raised OverflowError
dedup ok [3, 2, 1]
dedup-repeat wrong [2, 1]
counting ok [5, 4]
pushes 2
frozen raised TypeError
frozen-empty ok []
Stack True True
LimitedStack True False
DedupStack True False
CountingStack True False
FrozenStack True False
```

## Which subclasses break the contract?

- `CountingStack`: **safe**. It adds behaviour and keeps the promise (every push grows the stack,
  pop returns the last item).
- `LimitedStack`: **breaks it** by demanding more: the parent accepts any number of pushes,
  the child refuses after `limit`. A caller written for `Stack` has no reason to expect
  `OverflowError`. It only looked fine in `limit3` because the input was small enough.
- `DedupStack`: **breaks it** by promising less: after `push(1)` the length does not always grow
  and `pop()` does not always return the thing pushed.
- `FrozenStack`: **breaks it** completely: a stack that cannot be pushed to is not a `Stack`.

Fixes: do not inherit when the child cannot honour the parent's promises. Make `LimitedStack` a
separate class (or document a bounded `Stack` contract from the start), give `DedupStack` another
name and interface (`OrderedSet`), and for read-only data use a different type that has no `push`.
Prefer **composition** or a small shared Protocol (see p015).

## Another way

Check Liskov with a "contract test": write one test function that takes any `Stack` and verifies
the contract, then run it for every subclass. The failing subclasses are the ones that cannot
be substituted.
