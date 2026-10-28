# A list with undo and redo

A to-do app wants Ctrl+Z (undo) and Ctrl+Y (redo) for its list of tasks. Write `UndoableList` in
`solution.py`. It **wraps** a normal list (it has a list; it is not a subclass of `list`), so users
can only change it through methods that remember how to undo.

**`UndoableList(items=None)`**: starts with a **copy** of `items` (any iterable), or empty.

Changing methods (each one can be undone):

- `append(item)`: add at the end.
- `pop(index=-1)`: remove and return the item at `index` (negative indexes count from the end, as
  in a list). An empty list or a bad index raises `IndexError`.
- `set(index, value)`: replace the item at `index` (negative allowed). A bad index raises `IndexError`.
- `clear()`: remove everything.

Undo and redo:

- `undo()`: reverse the most recent change that has not been undone. With nothing to undo, raise
  `IndexError("nothing to undo")`.
- `redo()`: do again the most recently undone change. With nothing to redo, raise
  `IndexError("nothing to redo")`.
- Any **new** change (append, pop, set, clear) throws away everything that could be redone.
- A change that fails (raises) is not recorded.

Reading:

- `get(index)`, `size()`, and `to_list()` (a **new** list with the items).

The class must not offer the normal list methods like `sort` or `insert` (they could not be
undone), and it must not be a subclass of `list`.

**Example**

```python
u = UndoableList(["milk", "eggs"])
u.append("tea")
u.set(0, "oat milk")
u.pop(1)              # 'eggs'
u.to_list()           # ['oat milk', 'tea']
u.undo()              # puts 'eggs' back at index 1
u.undo()              # 'oat milk' becomes 'milk' again
u.to_list()           # ['milk', 'eggs', 'tea']
u.redo()
u.to_list()           # ['oat milk', 'eggs', 'tea']
u.append("rice")      # a new change: the undone pop cannot be redone any more
u.redo()              # IndexError: nothing to redo
```
