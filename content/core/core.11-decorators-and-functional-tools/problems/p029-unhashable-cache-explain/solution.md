## Approach

Start from how the cache works: a dict from arguments to results. Everything else follows. A
dict key must be hashable and must not change, so a list is refused. A cache only knows the
arguments, so anything else the function reads (a global, the clock) is invisible to it.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Think of the cache as a notebook with one line per question: "total of (10, 20, 30) = 60".
If the question could be rubbed out and rewritten after you wrote the answer, the notebook
would lie. And if the true answer depends on something not written in the question (today's
stock), the notebook goes stale.
