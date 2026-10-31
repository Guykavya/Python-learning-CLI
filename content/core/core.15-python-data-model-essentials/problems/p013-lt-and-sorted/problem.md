# Make objects sortable with __lt__

`sorted`, `list.sort`, `min` and `max` only need one thing from your objects: `a < b`.
Define `__lt__` and the whole family works.

`Task(priority, name)` is started for you (with `__eq__` and `__repr__`). A smaller priority number
means more urgent. Add `__lt__` so tasks sort by `priority`, and by `name` when priorities tie.

- `Task(1, "x") < Task(2, "a")` is `True`.
- Ties: `Task(2, "a") < Task(2, "b")` is `True`.
- Comparing with a non-`Task` returns `NotImplemented` (so `Task(1, "a") < 5` raises `TypeError`).

**Example**

```python
tasks = [Task(2, "b"), Task(1, "z"), Task(2, "a")]
print(sorted(tasks))    # [Task(1, 'z'), Task(2, 'a'), Task(2, 'b')]
print(max(tasks))       # Task(2, 'b')
print(Task(2, "a") > Task(1, "z"))   # True  (Python reflects > into <)
```
