## Approach

Sorting needs only `<`. Tuple comparison does the "then" logic. Returning `NotImplemented` for foreign types lets Python raise a clean `TypeError`.

## Code

```python
class Task:
    def __init__(self, priority, name):
        self.priority = priority
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, Task):
            return NotImplemented
        return (self.priority, self.name) == (other.priority, other.name)

    def __repr__(self):
        return f"Task({self.priority!r}, {self.name!r})"

    def __lt__(self, other):
        if not isinstance(other, Task):
            return NotImplemented
        return (self.priority, self.name) < (other.priority, other.name)
```

## Complexity

O(1) per comparison; sorting n tasks costs O(n log n) comparisons.

## Another way

Add `functools.total_ordering` (next problem) or give `sorted` a `key=` function when you cannot change the class.
