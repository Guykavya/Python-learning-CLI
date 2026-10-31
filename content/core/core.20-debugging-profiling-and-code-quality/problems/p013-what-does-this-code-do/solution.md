## Approach

The model answer is in `answer.md`. The method used to read the code:

1. **Run small cases by hand** and write down the variables per step. A table of `i`, `w` and
   `r` shows that `w` is always the sum of a window of `k` values.
2. **Name it.** Once you know it is a sliding-window average, the names
   `moving_average`, `values`, `window`, `window_sum`, `averages` make every line
   self-explaining.
3. **Count the outputs.** A good habit for any loop that produces a list: how many items
   should there be? `n - k + 1` windows, but the loop runs `n - k` times and appends before
   updating, so the last window is lost.
4. **Probe the edges**: zero, one, equal to the length, more than the length, negative.

## Check your answer

- Did you call it a moving (rolling) average and give clear names?
- Did you explain the O(1) slide (add the new value, subtract the old one)?
- Did you find that the **last** average is missing (`[3.0, 5.0, 7.0]` should end with `9.0`),
  and that `k = len(xs)` gives `[]`?
- Did you mention `ZeroDivisionError` for `k = 0` and `[]` for `k > len(xs)`?
- Does your fix append the first window before the loop (or after the update), and guard
  bad `k`?

## Another way

`statistics.fmean(values[i:i + window]) for i in range(len(values) - window + 1)` is the
obvious O(n·k) version: slower but nearly impossible to get wrong. A good debugging trick is to
keep it as a **test oracle**: compare the fast version against it on many random lists.
