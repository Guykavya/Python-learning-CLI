class QueueFromStacks:
    def __init__(self):
        self.inbox = []
        self.outbox = []

    def push(self, x):
        self.inbox.append(x)

    def pop(self):
        # TODO: this returns the NEWEST item, like a stack
        return self.inbox.pop()

    def peek(self):
        return self.inbox[-1]  # TODO

    def empty(self):
        return not self.inbox and not self.outbox
