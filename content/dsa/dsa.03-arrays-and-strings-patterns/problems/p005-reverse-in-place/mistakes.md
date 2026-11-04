- Looping `while i <= j`: harmless (the middle swaps with itself), but `i != j` as the condition is a bug: for
  even lengths `i` and `j` cross without ever being equal, so the loop keeps going past the middle, swaps pairs back
  and finally runs off the ends of the list.
- Looping `for i in range(l - 1, r)` and swapping `a[i]` with its mirror: every pair is swapped twice, so the
  part ends up unchanged. Stop at the middle.
- Swapping with two separate assignments `a[i] = a[j]; a[j] = a[i]`: the old `a[i]` is lost. Use the tuple swap.
- Forgetting that `l` and `r` are 1-based.
