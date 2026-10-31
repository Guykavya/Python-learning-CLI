- `for it in alive: ... alive.remove(it)` inside the same loop: changing a list while looping
  over it skips items.
- Calling `iter(x)` again in every round: a list then restarts, and you get its first item for ever.
- `zip(*iterables)`: stops when the shortest is done and loses the rest.
- Catching `StopIteration` but still yielding the old `value`.
- Converting each input to a list first: hangs on an endless source.
