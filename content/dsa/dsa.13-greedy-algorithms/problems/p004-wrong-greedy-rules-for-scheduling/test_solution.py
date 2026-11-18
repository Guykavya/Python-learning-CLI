from solution import wrong_rule_inputs


def pick(events, key):
    chosen = []
    last_end = float("-inf")
    for s, e in sorted(events, key=key):
        if s >= last_end:
            chosen.append((s, e))
            last_end = e
    return chosen


def earliest_start(ev):
    return (ev[0], ev[1])


def shortest_first(ev):
    return (ev[1] - ev[0], ev[0])


def brute_best(events):
    n = len(events)
    best = 0
    for mask in range(1 << n):
        chosen = sorted(events[i] for i in range(n) if mask >> i & 1)
        if all(chosen[i][1] <= chosen[i + 1][0] for i in range(len(chosen) - 1)):
            best = max(best, len(chosen))
    return best


CHAPTER = [sorted([(0, 10), (1, 2), (3, 4), (5, 6)]), sorted([(0, 5), (4, 7), (6, 10)])]


def check_valid(events, name):
    assert isinstance(events, (list, tuple)), f"{name} must be a list of (start, end) pairs, got {type(events).__name__}."
    assert 3 <= len(events) <= 8, f"{name} must have 3 to 8 events, it has {len(events)}."
    events = [tuple(ev) for ev in events]
    for ev in events:
        assert len(ev) == 2 and all(isinstance(x, int) for x in ev), (
            f"{name}: every event must be a pair of integers (start, end); {ev} is not.")
        assert ev[0] < ev[1], f"{name}: every event needs start < end; {ev} does not."
    assert sorted(events) not in CHAPTER, (
        f"{name} is one of the chapter's examples. Build your own: change the numbers and the number of events.")
    return events


def test_returns_a_pair():
    result = wrong_rule_inputs()
    assert isinstance(result, tuple) and len(result) == 2, "Return a pair (a, b) of two lists, for example `return a, b`."


def test_earliest_start_loses():
    a = check_valid(wrong_rule_inputs()[0], "a")
    greedy = len(pick(a, earliest_start))
    best = brute_best(a)
    assert greedy < best, (
        f"On a={a} earliest start picks {greedy} events and the best is also {best}: the rule did not lose. "
        "Make the event that starts first a LONG one that covers several short ones.")
    assert best - greedy >= 2, (
        f"On a={a} earliest start picks {greedy} events and the best is {best}: it must lose by at least 2. "
        "Let the long early event cover three or more short events.")


def test_shortest_first_loses():
    b = check_valid(wrong_rule_inputs()[1], "b")
    greedy = len(pick(b, shortest_first))
    best = brute_best(b)
    assert greedy < best, (
        f"On b={b} shortest first picks {greedy} events and the best is also {best}: the rule did not lose. "
        "Put a SHORT event across the boundary of two longer events that fit together, so taking it blocks both.")
