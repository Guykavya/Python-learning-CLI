class IndexedPQ:
    """A min-priority queue on a hand-written binary heap that knows where every key is."""

    def __init__(self):
        self.keys = []                       # keys[i] is the key at heap position i
        self.prios = []                      # prios[i] is its priority
        self.pos = {}                        # key -> its position in the arrays

    def __len__(self):
        return len(self.keys)

    def __contains__(self, key):
        return key in self.pos

    def stored(self):
        return len(self.keys)

    def peek(self):
        if not self.keys:
            raise IndexError("peek from an empty queue")
        return self.keys[0], self.prios[0]

    def priority(self, key):
        return self.prios[self.pos[key]]

    def push(self, key, priority):
        if key in self.pos:
            raise ValueError(f"{key!r} is already in the queue")
        self.keys.append(key)
        self.prios.append(priority)
        self.pos[key] = len(self.keys) - 1
        self._sift_up(len(self.keys) - 1)

    def update(self, key, priority):
        i = self.pos[key]
        self.prios[i] = priority
        self._restore(i)

    def remove(self, key):
        self._remove_at(self.pos[key])

    def pop_min(self):
        if not self.keys:
            raise IndexError("pop from an empty queue")
        item = (self.keys[0], self.prios[0])
        self._remove_at(0)
        return item

    # --- the heap machinery -------------------------------------------------

    def _swap(self, i, j):
        self.keys[i], self.keys[j] = self.keys[j], self.keys[i]
        self.prios[i], self.prios[j] = self.prios[j], self.prios[i]
        self.pos[self.keys[i]] = i
        self.pos[self.keys[j]] = j

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self.prios[i] < self.prios[parent]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i):
        n = len(self.keys)
        while True:
            smallest = i
            left, right = 2 * i + 1, 2 * i + 2
            if left < n and self.prios[left] < self.prios[smallest]:
                smallest = left
            if right < n and self.prios[right] < self.prios[smallest]:
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    def _restore(self, i):
        """The item at position i may be too small or too big for its place: move it the right way."""
        if i > 0 and self.prios[i] < self.prios[(i - 1) // 2]:
            self._sift_up(i)
        else:
            self._sift_down(i)

    def _remove_at(self, i):
        last = len(self.keys) - 1
        if i != last:
            self._swap(i, last)
        key = self.keys.pop()
        self.prios.pop()
        del self.pos[key]
        if i != last:
            self._restore(i)
