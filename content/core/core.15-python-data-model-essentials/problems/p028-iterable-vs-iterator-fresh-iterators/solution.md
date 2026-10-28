## Approach

The key question is *where the position is stored*. In `CountDown` it lives in the object that is also asked for the iterator, so it is shared and used up; in `Range3` each `iter()` call creates a new object that holds its own position.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Test your understanding by writing `class CountDown2` whose `__iter__` is a generator, and check `iter(c2) is c2` is `False` while `list(c2)` works twice.
