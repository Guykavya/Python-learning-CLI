- Forgetting the leftover. When the loop stops because `d * d > m`, the remaining `m` (if above 1) is
  a prime factor. Without it, `1999966` prints only `2`.
- Trying every `d` up to `n`. For a prime near 10^12 that is a trillion divisions, which never finishes.
- Comparing `d * d <= n` (the original number) instead of `<= m` (what is left). It is still correct,
  but it keeps looping long after `m` has become small, wasting time.
- Building the text with a `" * "` after every factor. The line then ends with `" * "`, which does
  not match the required output.
