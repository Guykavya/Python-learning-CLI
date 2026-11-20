## Approach

The model answer is in `answer.md`. A one-line memory aid: **A** all-or-nothing, **C** rules hold, **I** private until commit, **D** committed means kept.

You can watch two of the four in a terminal: raise an exception between the two `UPDATE`s of problem 19 (atomicity), and run problem 20 (isolation).

## Complexity

Not applicable.

## Another way

Explain it with a different story, such as booking a seat: A (seat taken and payment recorded together), C (no seat sold twice), I (two buyers do not see each other's half-done booking), D (the booking is still there after a restart).

## Why it matters

"Transaction" is a promise with four parts. Knowing which part prevents which failure tells you what to check when something goes wrong in production.
