import random

from solution import assign_rooms


def max_depth(meetings):
    """Largest number of meetings running at one moment (O(n^2) count at every start time)."""
    best = 0
    for t, _ in meetings:
        best = max(best, sum(1 for s, e in meetings if s <= t < e))
    return best


def check(meetings, rooms):
    meetings = [tuple(m) for m in meetings]
    assert isinstance(rooms, list) and len(rooms) == len(meetings), (
        f"Return a list with one room number per meeting ({len(meetings)} meetings); got {rooms!r}.")
    assert all(isinstance(r, int) for r in rooms), f"Room numbers must be ints; got {rooms}."
    used = set(rooms)
    assert used == set(range(len(used))), (
        f"meetings={meetings}: rooms used are {sorted(used)}; they must be 0 .. k-1 with no gaps.")
    for i in range(len(meetings)):
        for j in range(i + 1, len(meetings)):
            if rooms[i] == rooms[j]:
                a, b = meetings[i], meetings[j]
                assert not (a[0] < b[1] and b[0] < a[1]), (
                    f"meetings={meetings}, rooms={rooms}: {a} and {b} are both in room {rooms[i]} but overlap. "
                    "Reuse a room only if it is free (its last meeting ended at or before this start).")
    need = max_depth(meetings)
    assert len(used) == need, (
        f"meetings={meetings}, rooms={rooms}: you used {len(used)} rooms but the most meetings at one moment is "
        f"{need}, so {need} rooms are enough. Process meetings by START time and reuse the room that frees first; "
        "a room that frees at time t can be reused by a meeting starting at t.")


def test_chapter_examples():
    for meetings in ([(0, 30), (5, 10), (15, 20)], [(7, 10), (2, 4)], [(1, 5), (2, 6), (3, 7), (4, 8)]):
        check(meetings, assign_rooms(list(meetings)))


def test_touching_meetings_share_a_room():
    meetings = [(3, 5), (1, 3), (5, 7)]
    rooms = assign_rooms(meetings)
    check(meetings, rooms)
    assert rooms == [0, 0, 0], (
        "Touching meetings (1,3), (3,5), (5,7) fit in one room: a room freed at 3 can be used at 3 (use <=, not <).")


def test_rooms_follow_input_order():
    meetings = [(10, 12), (0, 11), (11, 13)]
    rooms = assign_rooms(meetings)
    check(meetings, rooms)
    assert rooms[0] != rooms[1], (
        "rooms[i] must belong to meetings[i] in the INPUT order. (10,12) and (0,11) overlap, so they need different "
        "rooms. Did you return the rooms in sorted order instead? Sort the indices, not the meetings.")


def test_edge_cases():
    assert assign_rooms([]) == [], "No meetings: an empty list."
    assert assign_rooms([(4, 9)]) == [0], "One meeting goes in room 0."
    meetings = [[1, 4], [1, 4], [1, 4]]
    check(meetings, assign_rooms(meetings))


def test_input_not_changed():
    data = [(0, 30), (5, 10), (15, 20)]
    assign_rooms(data)
    assert data == [(0, 30), (5, 10), (15, 20)], "Do not sort the caller's list in place."


def test_random_against_depth():
    rng = random.Random(10)
    for _ in range(500):
        n = rng.randint(0, 9)
        meetings = []
        for _ in range(n):
            s = rng.randint(0, 15)
            meetings.append((s, s + rng.randint(1, 6)))
        check(meetings, assign_rooms(list(meetings)))


def test_large_input_is_fast():
    meetings = [(i, i + 3) for i in range(100_000)]
    rooms = assign_rooms(meetings)
    assert len(set(rooms)) == 3, "Meetings (i, i+3): 3 run at once, so 3 rooms. Use a heap, not a scan of every room."
    assert rooms[0] == rooms[3], "(0,3) and (3,6) touch: with the fewest rooms, (3,6) must reuse (0,3)'s room."
