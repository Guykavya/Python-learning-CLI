## Approach

Start from the idea of a position that only moves forward: a generator is one pass, and the first
`sum` used it up. Then compare the two built-ins on empty input, and finish with a practical rule.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Show the state with `next(big, "empty")` after the first `sum`: it prints `empty`, which proves
the generator has nothing left before `max` is even called.
