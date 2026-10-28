## Approach

Keep track of which generator is active.

| Call | What happens | Prints |
|---|---|---|
| `next(g)` | `outer` starts and enters `inner("A")`, which pauses at `yield total` with 0 | `A starts`, `0` |
| `send(5)` | goes through `yield from` to A: `total` = 5 | `A got 5`, `5` |
| `send(3)` | A: `total` = 8 | `A got 3`, `8` |
| `next(g)` | A gets `None`, breaks, returns 8. `a = 8` in `outer`. `outer` goes on and starts `inner("B")`, which yields 0 | `A ends`, `A returned 8`, `B starts`, `0` |
| `send(10)` | goes to B: `total` = 10 | `B got 10`, `10` |
| `next(g)` | B returns 10. `b = 10`. `outer` reaches `yield a + b` | `B ends`, `B returned 10`, `18` |
| `next(g)` | `outer` resumes, prints, returns `"ok"`. That raises `StopIteration("ok")` | `outer done`, `finished ok` |

The key moment is the fourth call. One `next(g)` does a lot of work: it ends A, runs the code in
`outer` between the two `yield from` lines, and starts B. It only stops at the next real `yield`.

## Output

```text
A starts
0
A got 5
5
A got 3
8
A ends
A returned 8
B starts
0
B got 10
10
B ends
B returned 10
18
outer done
finished ok
```

## Complexity

O(1): a fixed number of steps.

## Another way

Write `outer` without `yield from`: a `while True` loop that calls `sub.send(value)`, yields the
result, and catches `StopIteration as e` to read `e.value`. That loop is roughly what `yield from`
does for you. It also shows why the return value travels inside `StopIteration`: the generator has
no other way to hand it back.
