from collections import deque


class StackFromQueue:
    def __init__(self, queue_factory=deque):
        self.q = queue_factory()

    def push(self, x):
        self.q.append(x)

    def pop(self):
        return self.q.pop()       # TODO: pop() from the back is not a queue operation

    def top(self):
        return self.q[-1]         # TODO: q[-1] is not a queue operation either

    def empty(self):
        return not self.q
