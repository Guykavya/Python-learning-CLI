## Approach

Map each piece of the comprehension to `map` or `filter`, then use the iterator idea from core.10 to explain
the empty second list. Finish with a readability rule rather than a speed rule.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer. (All the versions shown are O(n).)

## Another way

Run `m = map(abs, [-1, 2])`, then `next(m)`, `next(m)`, `next(m)`. The third call raises `StopIteration`,
which shows directly that `map` is an iterator.
