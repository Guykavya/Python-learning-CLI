import pytest

from solution import simulate

HEAVY_FIRST = [6, 1, 1, 1, 1, 1, 1, 1]


def test_round_robin_stacks_requests_behind_the_heavy_one():
    assert simulate("round_robin", HEAVY_FIRST, 2) == {"requests": [4, 4], "busy": [9, 4], "max_wait": 4}, \
        "Round robin gives server 0 requests 0, 2, 4, 6: the heavy one plus three more that wait behind it (the request at time 2 waits until 6)."


def test_least_connections_avoids_the_busy_server():
    assert simulate("least_connections", HEAVY_FIRST, 2) == {"requests": [3, 5], "busy": [8, 5], "max_wait": 0}, \
        "While the heavy request is in flight on server 0 (it ends at 6), requests 1 to 5 all go to server 1; at time 6 both are idle and the tie goes to server 0, which takes requests 6 and 7."


def test_equal_requests_are_spread_evenly_by_both():
    for policy in ("round_robin", "least_connections"):
        got = simulate(policy, [3] * 9, 3)
        assert got == {"requests": [3, 3, 3], "busy": [9, 9, 9], "max_wait": 0}, f"{policy}: identical requests that each take 3 units on 3 servers need no queues: {got}"


def test_ties_go_to_the_lowest_numbered_server():
    got = simulate("least_connections", [1, 1, 1], 3)
    assert got["requests"] == [3, 0, 0], "Every request ends before the next arrives, so all three servers always look equal: the tie goes to server 0."


def test_in_flight_means_end_time_greater_than_now():
    # request 0 (duration 1) ends at time 1, exactly when request 1 arrives: it is no longer in flight.
    assert simulate("least_connections", [1, 5], 2)["requests"] == [2, 0], \
        "At time 1 server 0's request has just ended (end 1 is not greater than 1), so server 0 is free and wins the tie."


def test_a_long_run_of_slow_requests_shows_the_difference_in_waiting():
    durations = [8, 1] * 4                           # a heavy and a light request alternating, on 2 servers
    rr = simulate("round_robin", durations, 2)
    lc = simulate("least_connections", durations, 2)
    assert rr["busy"] == [32, 4], "Round robin sends every heavy request to server 0 (all the even positions)."
    assert lc["max_wait"] < rr["max_wait"], f"Least connections must wait less than round robin here: {lc['max_wait']} vs {rr['max_wait']}"
    assert sum(rr["busy"]) == sum(lc["busy"]) == sum(durations), "The total work is the same; only its distribution changes."


def test_one_server_gets_everything():
    got = simulate("round_robin", [2, 2, 2], 1)
    assert got == {"requests": [3], "busy": [6], "max_wait": 2}, f"One server, three requests of 2 arriving at 0, 1, 2: they start at 0, 2, 4 and wait 0, 1, 2 units; got {got}"


def test_no_requests():
    assert simulate("least_connections", [], 3) == {"requests": [0, 0, 0], "busy": [0, 0, 0], "max_wait": 0}


@pytest.mark.parametrize("policy, servers", [("random", 2), ("round_robin", 0), ("least_connections", -1)])
def test_bad_input(policy, servers):
    with pytest.raises(ValueError):
        simulate(policy, [1, 2], servers)
