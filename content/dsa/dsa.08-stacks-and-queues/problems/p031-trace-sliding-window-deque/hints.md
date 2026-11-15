## Hint 1

First run, `i = 1`, value 3: the back holds index 0 (value 1), and `1 <= 3`, so it is popped. The deque is `[1]`. At `i = 2` (value -1) nothing is popped; the deque is `[1, 2]` and the first window `[1, 3, -1]` is complete: maximum `nums[1] = 3`.

## Hint 2

Second run: `5, 4, 3` are decreasing, so nothing is popped from the back and the deque is `[0, 1, 2]` at `i = 2`. At `i = 3` (value 2) the back value 3 is greater, so 3 is appended; then the front index 0 satisfies `0 <= 3 - 3`. What happens to it?
