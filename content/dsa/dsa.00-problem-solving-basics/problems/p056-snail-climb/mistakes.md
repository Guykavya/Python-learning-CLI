- Using `h / (u - d)`. That ignores the last climb (on the final day there is no slide), so the
  answer is too large, and `/` gives a float that is inexact near 10^18.
- Using `(h - u) // (u - d) + 1` (floor instead of ceiling). When the division is not exact the
  snail is still short and needs one more day: `10 3 1` gives 4 instead of 5.
- Checking `u <= d` before `u >= h`. For `5 5 100` the snail escapes on day 1, but the program says
  `never`.
- Simulating day by day. It is correct but for `h = 10^18, u = 2, d = 1` it needs about 10^18 steps.
