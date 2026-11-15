## Approach

Check the two rules separately. A missing base case (A) is visible at a glance. A base case that can be skipped (B) shows up only when you try several inputs, here odd ones. No progress (C) means the argument passed down is "as big as" the original. A sound function (D) has both.

## Model answer

See `answer.md`: the labels are **1-A, 2-B, 3-C, 4-D**.

## What to check

- Your reason for 2 mentions odd numbers and the value `-1`.
- Your reason for 3 mentions that `xs[:]` copies the whole list.
- Your fixes would really stop: run them on `evens(5)` and `length([1, 2, 3])`.
- Your explanation of the limit mentions the call stack and `RecursionError`.

## Another way

You can also prove termination with a **measure**: a whole number that is never negative and gets strictly smaller at every call (`n` for snippet 4's digit count, `len(xs)` for a correct `length`). If no such measure exists, the recursion may not stop.
