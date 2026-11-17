## Hint 1

When two tuples `(1, a)` and `(1, b)` are compared, Python looks at the first elements (equal), then at the second ones. If the second element were a number that is **different for every entry**, the comparison would end there and never reach the task. Which number is different for every `add`, and grows with each one?

## Hint 2

Give every queue a counter, for example `itertools.count()`, and call `next(counter)` in `add`. The entry is `(priority, next(counter), task)`. Because the counter grows, an earlier `add` has a smaller counter, so among equal priorities the first one comes out first. `pop` takes the tuple from `heappop` and returns only its last element.

## Hint 3

```
__init__:  self._heap = [];  self._counter = itertools.count()
add(priority, task):  heappush(self._heap, (priority, next(self._counter), task))
pop():                priority, _, task = heappop(self._heap);  return task      # IndexError if empty
__len__:              len(self._heap)
```
