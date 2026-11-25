## Approach

Separate **exploring** from **deciding**. Slicing a flat result finds noise; a decision needs a pre-planned question or a new test.

## Code

See `answer.md`.

## Complexity

Not applicable (an explain problem).

## Another way

If you must look at segments in the same test, test the **interaction** (does the effect differ by segment?) once, and correct the segment p-values for the number of looks (Bonferroni or false-discovery-rate).
