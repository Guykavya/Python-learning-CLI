- Describing the code line by line ("it appends w / k to r") instead of saying what it
  **computes**. The reader needs the purpose first.
- Missing the off-by-one because the example output "looks like averages". Count the windows.
- Thinking `k > len(xs)` crashes. Slicing past the end is allowed; the loop simply does not run.
- Fixing the bug by changing the loop to `range(k, len(xs) + 1)`. Then `xs[i]` goes past the
  end on the last step (`IndexError`).
- Fixing by appending `w / k` after the loop without a guard: for `k > len(xs)` that returns the
  average of a too-short window.
- Renaming without checking behaviour. Readable code with the same bug is still buggy.
