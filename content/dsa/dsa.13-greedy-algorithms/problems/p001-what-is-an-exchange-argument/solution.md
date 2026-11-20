## Approach

Follow the five-step template of chapter section 3 with the concrete objects of activity selection: an optimal schedule `O`, its first event `f`, greedy's first event `g`, and `O`'s second event `h`. Every step becomes one inequality between start and end times.

## Model answer

See `answer.md`.

## What to check

- You started from an **arbitrary** optimal answer. Starting from greedy's own answer proves nothing.
- You proved **both** parts of the swap: still valid (no overlap) and no worse (same count).
- You said "there exists an optimal answer containing `g`", not "greedy's answer is the only optimum".
- You named the step that breaks for the wrong rule (validity), with the numbers.

## Another way

The **stay-ahead** argument (chapter section 4) proves the same algorithm differently: show by induction that greedy's `i`-th event ends no later than the optimal schedule's `i`-th event. Then greedy can never run out of room before the optimal schedule does. Try writing it in four sentences and compare which picture you find easier.
