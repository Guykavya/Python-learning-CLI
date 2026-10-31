from dataclasses import dataclass, field


@dataclass
class Cart:
    owner: str
    items: list = field(default_factory=list)

    def add(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)


@dataclass
class Tags:
    names: set = field(default_factory=set)

    def add(self, name):
        self.names.add(name.lower())


@dataclass
class Counter:
    counts: dict = field(default_factory=dict)

    def hit(self, key):
        self.counts[key] = self.counts.get(key, 0) + 1
