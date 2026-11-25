## Approach

The model answer is in `answer.md`. Mean and standard deviation compress 20 numbers into 2; many different datasets share the same two numbers (Anscombe's quartet is the famous example), so the picture and a few robust numbers must come first.

## Code

No code. You can reproduce the idea with `statistics` by building a list of 19 similar values plus one far value and comparing the mean and the median.

## Complexity

Not applicable.

## Another way

Overlay the four histograms on one axis, or draw four box plots: the five-number summary alone (min, Q1, median, Q3, max) already separates B, C and D from A.
