from collections import deque


class Scheduler:
    def __init__(self, quantum, capacity):
        if quantum <= 0:
            raise ValueError("quantum must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.quantum = quantum
        self.capacity = capacity
        self.ready = deque()
        self.clock = 0
        self.finished = []

    def submit(self, name, work):
        if work <= 0:
            raise ValueError("work must be positive")
        if len(self.ready) >= self.capacity:
            return False
        self.ready.append((name, work))
        return True

    def step(self):
        if not self.ready:
            return None
        name, left = self.ready.popleft()
        run = min(self.quantum, left)
        self.clock += run
        left -= run
        if left:
            self.ready.append((name, left))
        else:
            self.finished.append((name, self.clock))
        return name

    def run_all(self):
        while self.ready:
            self.step()
        return list(self.finished)

    def __len__(self):
        return len(self.ready)
