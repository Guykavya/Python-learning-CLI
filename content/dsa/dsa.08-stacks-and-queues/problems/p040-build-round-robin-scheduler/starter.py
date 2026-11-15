from collections import deque


class Scheduler:
    def __init__(self, quantum, capacity):
        self.quantum = quantum
        self.capacity = capacity
        self.ready = deque()
        self.clock = 0
        self.finished = []

    def submit(self, name, work):
        # TODO: validate, respect the capacity, return True/False
        return False

    def step(self):
        # TODO: run the front job for one slice
        return None

    def run_all(self):
        # TODO
        return list(self.finished)

    def __len__(self):
        return len(self.ready)
