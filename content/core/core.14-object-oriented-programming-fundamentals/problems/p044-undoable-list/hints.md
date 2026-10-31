## Hint 1

What must you remember about each change to be able to reverse it later? For `append`: nothing
much (undo is "remove the last item"). For `pop(i)`: the item **and** where it was. For `set`: the
old value and where. For `clear`: all the old items. Keep these records on a stack: the last change
is undone first.

## Hint 2

Redo needs a second stack. `undo` moves a record from the undo stack to the redo stack (after
reversing it); `redo` moves it back (after doing it again). A new change pushes onto the undo stack
and **empties** the redo stack.

Turn a negative index into the real position **before** you record it: `-1` means a different
place once the list has changed. `real = index + len(items) if index < 0 else index`, and check
`0 <= real < len(items)`.

## Hint 3

```
__init__: self._items = copy of items; self._undo = []; self._redo = []

pop(index):
    real = self._index(index)          # raises IndexError, nothing recorded
    item = self._items.pop(real)
    record(("pop", real, item)); return item

record(change): self._undo.append(change); self._redo.clear()

undo():
    if not self._undo: raise IndexError("nothing to undo")
    change = self._undo.pop(); reverse(change); self._redo.append(change)

reverse(change):
    append -> self._items.pop()
    pop    -> self._items.insert(real, item)
    set    -> self._items[real] = old
    clear  -> self._items[:] = old_items
```
