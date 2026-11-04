- Starting `cur` and `best` at 0. For `-3 -1 -2` that prints 0, which is the sum of the empty subarray; the answer is -1.
- Resetting with `if cur < 0: cur = 0` **before** updating `best`: the same bug as above in another form. If you
  reset, update `best` with `cur + x` first.
- Returning the final `cur` instead of `best`. `cur` is only the best run that ends at the last element.
- Taking the sum of all positive elements: that is the best *subsequence* (elements need not be neighbours), not the
  best subarray.
