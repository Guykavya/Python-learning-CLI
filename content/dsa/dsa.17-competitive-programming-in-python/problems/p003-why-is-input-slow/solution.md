## Approach

This is an explanation problem: the model answer is in `answer.md`. The key sentence is: *the cost of `input()` is per call, the data is already buffered, and `read().split()` replaces 200 000 Python-level calls with one call and C loops.*

You can see the difference on your own machine with the timing harness of chapter section 3: time program A and program B on a generated file with 200 000 numbers.

## Complexity

All three readers are `O(n)` in the amount of data. They differ only in the **constant** per line, which is what contests measure.

## Another way

Explain it with a postal analogy: `input()` is going to the post office for every letter; `readline` is going to the mailbox for every letter; `read()` is carrying the whole sack home once.
