## Approach

Give each wrong rule a **tempting but bad** first choice (chapter section 3: "one huge item among small ones").

- **Earliest start** is tempted by an event that starts first. Make it long, so it covers several short events: `a = [(0, 20), (2, 4), (5, 7), (8, 10), (11, 13)]`. Earliest start takes `(0, 20)` and nothing else fits: 1 event. The best takes the four short ones: 4 events.
- **Shortest first** is tempted by a short event. Put it across the boundary of two longer events: `b = [(0, 6), (7, 13), (14, 20), (21, 27), (5, 8), (19, 22)]`. Shortest first takes `(5, 8)` and `(19, 22)` (length 3 each); each one overlaps two long events, so nothing else fits: 2 events. The best takes the four long events: 4 events.

```python
def wrong_rule_inputs():
    a = [(0, 20), (2, 4), (5, 7), (8, 10), (11, 13)]
    b = [(0, 6), (7, 13), (14, 20), (21, 27), (5, 8), (19, 22)]
    return a, b
```

## Complexity

The function returns constants. The test's brute force tries `2^n` subsets, which is why the lists are limited to 8 events.

## Another way

Let the computer find them (chapter section 15): generate thousands of random lists of 4 to 6 events with a fixed `random.Random(seed)`, run `pick` with the wrong key and the brute force, and keep the first list where they differ. Hand-made examples are easier to understand; random search finds the strange ones, like the ten-interval example that breaks "fewest conflicts first".
