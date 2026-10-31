from dataclasses import dataclass, field

SHARED_COUNTS = {}


class Cart:
    def __init__(self, owner, items=[]):
        self.owner = owner
        self.items = items

    def add(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)


@dataclass
class Tags:
    names: set = field(default_factory=set())

    def add(self, name):
        self.names.add(name.lower())


@dataclass
class Counter:
    counts: dict = field(default_factory=lambda: SHARED_COUNTS)

    def hit(self, key):
        self.counts[key] = self.counts.get(key, 0) + 1
