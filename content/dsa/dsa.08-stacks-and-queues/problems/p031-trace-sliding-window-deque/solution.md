## Approach

Keep the deque of indices with values decreasing from front to back. The back pops remove values that can never be a maximum again (they are older and not larger than the new value). The front pop removes the index that has slid out of the window.

## Expected output

```text
0 [0] -
1 [1] -
2 [1, 2] 3
3 [1, 2, 3] 3
4 [4] 5
5 [4, 5] 5
6 [6] 6
7 [7] 7
next
0 [0] -
1 [0, 1] -
2 [0, 1, 2] 5
3 [1, 2, 3] 4
4 [4] 6
5 [4, 5] 6
```

## Why

- First run: larger values keep arriving and clear the deque from the back (at `i = 4` the 5 pops `-3`, `-1` and `3`; at `i = 6` the 6 pops `3` and `5`), so the front index never gets old enough to expire. This matches the chapter's table.
- Second run: `5, 4, 3, 2` are strictly decreasing, so nothing leaves from the back. At `i = 3` the deque would be `[0, 1, 2, 3]`, but index 0 is `<= 3 - 3`: it has left the window `[4, 3, 2]` and is removed from the front. Without that check the program would report 5 instead of 4.
- At `i = 4` the 6 clears the whole deque from the back.

The front always holds the largest value in the window, because every value behind it is smaller (the deque is decreasing) and every larger, older value has already been removed.
