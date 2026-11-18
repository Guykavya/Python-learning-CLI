# Wrong greedy rules for scheduling

Proving a greedy rule is one half of the skill; **breaking** a wrong rule is the other, and it is much cheaper (chapter section 3, "try to break it"). Here you break two rules for activity selection (choose the most events with no overlap; touching is fine).

The test runs this greedy with two different keys:

```python
def pick(events, key):
    chosen = []
    last_end = float("-inf")
    for s, e in sorted(events, key=key):
        if s >= last_end:
            chosen.append((s, e))
            last_end = e
    return chosen

earliest_start = lambda ev: (ev[0], ev[1])            # start first; ties by end
shortest_first = lambda ev: (ev[1] - ev[0], ev[0])    # length first; ties by start
```

Write `wrong_rule_inputs()` that returns a pair `(a, b)` of two lists of events:

- on `a`, **earliest start** chooses **fewer** events than the true best;
- on `b`, **shortest first** chooses **fewer** events than the true best.

The test finds the true best by trying every subset.

## Rules for your inputs

- Each list has **3 to 8** events. Each event is a pair `(start, end)` of integers with `start < end` (no empty events).
- Do **not** return the chapter's examples. The test rejects `[(0, 10), (1, 2), (3, 4), (5, 6)]` and `[(0, 5), (4, 7), (6, 10)]`, in any order. Build your own.
- On `a`, earliest start must lose by **at least 2** events (not only one).

## Example

This is **not** an answer (both rules choose the best here); it only shows the shape:

```python
>>> a, b = wrong_rule_inputs()
>>> a
[(1, 3), (4, 6), (7, 9)]
```

## Think about

What does each wrong rule find "tempting"? Earliest start is tempted by an event that starts early, whatever its end. Shortest first is tempted by a short event, wherever it sits. Make the tempting event a bad one.
