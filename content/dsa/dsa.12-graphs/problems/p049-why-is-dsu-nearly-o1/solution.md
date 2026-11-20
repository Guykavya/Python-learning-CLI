## Approach

Prove what you can with counting, and quote what you cannot. The `O(log n)` bound for union by size has a short, complete proof (the doubling argument): it is the heart of the answer. Path compression's extra gain down to α(n) has a long proof that no course at this level asks for; it is enough to explain what compression does, what "amortised" means, and why α can be treated as a constant.

Use the chapter's measurement as the anchor: 100,000 unions along a line give a chain of depth 99,999 without the tricks and depth 1 with them.

## Model answer

See `answer.md`.

## What to check

- Your doubling argument says **why** the group doubles (only the smaller group is moved down) and **why** that limits the depth (a group cannot double more than `log2 n` times).
- You separated the two tricks: union by size alone gives `O(log n)`, compression flattens paths, and both together give `O(α(n))` amortised.
- You explained "amortised" as a statement about a whole sequence, and said that one call can still be slower.
- You did not claim that every single `find` takes one step.
- You named a real limit (no splitting, no fast listing) and when BFS is the better tool.

## Another way to see the doubling argument

Track one element `x` from the start. It begins in a group of size 1 at depth 0. Write down its depth and its group size after every union that moves it down: `(1, >= 2)`, `(2, >= 4)`, `(3, >= 8)`, ... After `d` moves the group has at least `2^d` elements, and it can never have more than `n`. So `2^d <= n`, that is `d <= log2(n)`.
