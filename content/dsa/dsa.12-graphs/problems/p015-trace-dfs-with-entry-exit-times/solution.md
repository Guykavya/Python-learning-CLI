## Approach

Keep the call stack on paper. Every `enter` reads the clock and adds one; every `exit` does the same after the `for` loop of that vertex has finished.

## Expected output

```text
enter 0 at 0
enter 1 at 1
enter 2 at 2
enter 3 at 3
exit 3 at 4
exit 2 at 5
exit 1 at 6
enter 4 at 7
enter 5 at 8
exit 5 at 9
exit 4 at 10
exit 0 at 11
0 0 11
1 1 6
2 2 5
3 3 4
4 7 10
5 8 9
```

## Why

The call stack grows `0 -> 1 -> 2 -> 3`. In `3`, both neighbours `1` and `2` are on the stack (visited), so `3` exits at 4, then `2` at 5. Back in `1`, the loop's last neighbour is `3`, which was visited through `2`, so `1` exits at 6. `0` then goes to `4` and `5`.

As brackets: `(0 (1 (2 (3 3) 2) 1) (4 (5 5) 4) 0)`. The subtree of `1` is `{1, 2, 3}`: their intervals `[2, 5]` and `[3, 4]` lie inside `[1, 6]`. The intervals of `4` and `5` lie outside it.

## Another way

The iterative `dfs_enter_exit` of the chapter produces the same events with a stack of iterators: an event is printed when a vertex is pushed (enter) and when its iterator is used up (exit).
