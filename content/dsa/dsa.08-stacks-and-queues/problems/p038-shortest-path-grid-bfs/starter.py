from collections import deque


def shortest_path(grid, start, goal):
    queue = deque([(start[0], start[1], 0)])
    seen = {start}
    # TODO: BFS; mark neighbours as seen when you enqueue them
    return -1
