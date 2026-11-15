class MinStack:
    def __init__(self):
        self.items = []

    def push(self, x):
        self.items.append(x)

    def pop(self):
        return self.items.pop()

    def top(self):
        return self.items[-1]

    def get_min(self):
        # TODO: return the minimum in O(1) (no scan); raise IndexError on an empty stack
        return 0
