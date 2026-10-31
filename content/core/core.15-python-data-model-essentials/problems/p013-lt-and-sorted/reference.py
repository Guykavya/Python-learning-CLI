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
