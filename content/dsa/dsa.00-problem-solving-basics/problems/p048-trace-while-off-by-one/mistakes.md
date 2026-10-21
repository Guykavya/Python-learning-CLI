- Printing the value `i` had at the start of the iteration in loops B and C. There the increment
  comes first, so the printed value is already one larger.
- Stopping loop B at `B 3`. With `<=`, the check `3 <= 3` is still true, so one more pass runs
  and prints `B 4`.
- Thinking the counter after the loop equals the last printed value. In loop A the last print is
  `A 2` but `i` ends at 3: the loop stops only after `i` has moved past the limit.
