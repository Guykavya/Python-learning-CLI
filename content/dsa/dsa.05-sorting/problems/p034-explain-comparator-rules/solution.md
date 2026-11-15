## Approach

Use the three rules as a checklist: antisymmetry, transitivity, and that 'equal' behaves like a real equivalence.

## Model answer

See `answer.md`. Compare it with yours point by point.

## What to check

- `key=` is called `n` times; `cmp_to_key` calls the comparator on each comparison.
- All three rules are named and a violated rule is identified (transitivity for rock-paper-scissors).
- The sort with such a comparator terminates but returns an unspecified order.
- Negation works for numbers only; for strings use two stable sorts, or `reverse=True`, or compare tuples of ordinals.
