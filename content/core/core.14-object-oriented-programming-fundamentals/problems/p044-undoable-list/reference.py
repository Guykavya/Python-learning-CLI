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
