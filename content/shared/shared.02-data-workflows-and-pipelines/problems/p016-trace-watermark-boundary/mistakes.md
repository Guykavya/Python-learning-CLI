- Thinking `gt` picks up order 3 in run 2. Its watermark is 105 and `105 > 105` is false: a row
  that arrives late with the boundary timestamp is skipped forever.
- Counting a re-fetched, unchanged row as `changed`. `ge` receives order 2 again in run 2, but its
  stored value is still 105, so it adds 0.
- Moving the watermark when nothing was fetched. `if ids:` protects it; `gt` keeps 107 in run 3.
- Forgetting that `ge` re-fetches the boundary row every run (`[4]` in run 3) and that `overlap`
  re-fetches its whole window (`[2, 3, 4]`).
- Applying the overlap to the comparison sign: `overlap` uses `t > wm - 3`, so with wm 107 the
  lower bound is 104, and 105 is inside.
- Thinking the overlap window catches order 5 (t = 103). 103 is not greater than 104.
- Printing `None` for the watermark after run 1, or the wrong list format (`[]` for empty).
