import heapq


def assign_rooms(meetings):
    """rooms[i] = room number (0, 1, 2, ...) of meetings[i], using the fewest rooms."""
    order = sorted(range(len(meetings)), key=lambda i: meetings[i][0])
    rooms = [0] * len(meetings)
    busy = []                      # min-heap of (end time, room number) for rooms in use
    opened = 0
    for i in order:
        s, e = meetings[i]
        if busy and busy[0][0] <= s:              # the room that frees first is free by now
            _, room = heapq.heappop(busy)
        else:
            room = opened                         # every room is busy: open a new one
            opened += 1
        rooms[i] = room
        heapq.heappush(busy, (e, room))
    return rooms
