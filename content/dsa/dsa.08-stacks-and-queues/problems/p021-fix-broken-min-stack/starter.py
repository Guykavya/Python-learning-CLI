class MinStack:
    def __init__(self):
        self.items = []
        self.mins = []          # each value that was a new minimum when it arrived

    def push(self, x):
        self.items.append(x)
        if not self.mins or x < self.mins[-1]:
            self.mins.append(x)

    def pop(self):
        x = self.items.pop()
        if x == self.mins[-1]:
            self.mins.pop()
        return x

    def top(self):
        return self.items[-1]

    def get_min(self):
        return self.mins[-1]
