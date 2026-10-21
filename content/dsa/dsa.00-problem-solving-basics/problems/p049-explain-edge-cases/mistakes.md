- Listing edge cases without expected outputs. An edge case is only useful if you know what the
  right answer is before running the program.
- Saying the attempt "fails for negatives" without being exact: it fails when **all** values are
  negative (largest wrongly 0), and when all are positive (smallest wrongly 0).
- Ignoring `n = 0` because "nobody would type that". Empty input is the most common real-world
  edge case, and here it crashes the program.
- Testing only "typical" inputs like the given example, which hide the bug because they contain
  both positive and negative values.
