## Approach

**Composition, not inheritance** (chapter section 14). If `UndoableList` inherited from `list`, it
would also get `sort`, `insert`, `extend`, `remove`, `+=` and `u[0] = ...`, and none of those would
record an undo step. Users could change the list behind the undo system's back. Wrapping a private
list in `self._items` and offering only our own methods closes that door. This is the same
"Stack(list) leak" the chapter warns about.

**Records on two stacks.** Every successful change pushes a small tuple that holds what is needed to
reverse **and** to repeat it:

| change | record | undo | redo |
|---|---|---|---|
| `append(x)` | `("append", x)` | pop the last item | append `x` |
| `pop(i)` | `("pop", real_i, item)` | insert `item` at `real_i` | pop at `real_i` |
| `set(i, v)` | `("set", real_i, old, v)` | put `old` back | put `v` back |
| `clear()` | `("clear", old_items)` | restore `old_items` | clear |

`undo` moves the top record to the redo stack; `redo` moves it back. A new change clears the redo
stack, because the undone future no longer fits the new present.

**Real indexes.** `pop(-3)` on `[1, 2, 3, 4]` removes index 1. If we recorded `-3`, undo would
insert at `-3` of `[1, 3, 4]`, which is index 0: wrong place. So `_index` converts first, and it
also raises `IndexError` before anything is changed or recorded.

## Code

```python
class UndoableList:
    def __init__(self, items=None):
        self._items = [] if items is None else list(items)
        self._undo = []      # records of changes that can be undone
        self._redo = []      # records of undone changes that can be redone

    # ---- helpers -------------------------------------------------------

    def _index(self, index):
        """Turn a possibly negative index into a real position, or raise IndexError."""
        n = len(self._items)
        real = index + n if index < 0 else index
        if not 0 <= real < n:
            raise IndexError("list index out of range")
        return real

    def _record(self, change):
        self._undo.append(change)
        self._redo.clear()           # a new change ends the redo chain

    def _apply(self, change):
        kind = change[0]
        if kind == "append":
            self._items.append(change[1])
        elif kind == "pop":
            self._items.pop(change[1])
        elif kind == "set":
            self._items[change[1]] = change[3]
        elif kind == "clear":
            self._items.clear()

    def _reverse(self, change):
        kind = change[0]
        if kind == "append":
            self._items.pop()
        elif kind == "pop":
            self._items.insert(change[1], change[2])
        elif kind == "set":
            self._items[change[1]] = change[2]
        elif kind == "clear":
            self._items[:] = change[1]

    # ---- changing methods ----------------------------------------------

    def append(self, item):
        self._items.append(item)
        self._record(("append", item))

    def pop(self, index=-1):
        real = self._index(index)
        item = self._items.pop(real)
        self._record(("pop", real, item))
        return item

    def set(self, index, value):
        real = self._index(index)
        old = self._items[real]
        self._items[real] = value
        self._record(("set", real, old, value))

    def clear(self):
        old = list(self._items)
        self._items.clear()
        self._record(("clear", old))

    # ---- undo / redo ----------------------------------------------------

    def undo(self):
        if not self._undo:
            raise IndexError("nothing to undo")
        change = self._undo.pop()
        self._reverse(change)
        self._redo.append(change)

    def redo(self):
        if not self._redo:
            raise IndexError("nothing to redo")
        change = self._redo.pop()
        self._apply(change)
        self._undo.append(change)

    # ---- reading --------------------------------------------------------

    def get(self, index):
        return self._items[self._index(index)]

    def size(self):
        return len(self._items)

    def to_list(self):
        return list(self._items)
```

Undo and redo always happen in the reverse order of each other, so the list is in exactly the state
it had when the change was first made. That is why storing the real index is enough.

## Complexity

`append`, `set`, `undo`/`redo` of those are O(1). `pop(i)` and its undo are O(n) (a list shifts the
items after `i`). `clear` and its undo copy the list: O(n).

## Another way

**Snapshots:** before every change, push `list(self._items)` on the undo stack; undo pops a snapshot
and restores it. It is much shorter and impossible to get wrong, but every change costs O(n) memory.
For short lists that is fine. The record version scales to big lists. In the challenge problems you
will turn each record into a small `Command` object with its own `do()` and `undo()` methods.
