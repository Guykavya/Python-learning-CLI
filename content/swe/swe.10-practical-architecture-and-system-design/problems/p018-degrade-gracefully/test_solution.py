import pytest

from solution import POPULAR, CircuitBreaker, recommendations


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class Primary:
    """The recommendation service: scripted answers, and a log of how it was called."""

    def __init__(self, *outcomes):
        self.outcomes, self.calls, self.timeouts = list(outcomes), 0, []

    def __call__(self, user, timeout):
        self.calls += 1
        self.timeouts.append(timeout)
        outcome = self.outcomes.pop(0) if len(self.outcomes) > 1 else self.outcomes[0]
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def breaker(clock):
    return CircuitBreaker(failure_threshold=3, reset_after=10.0, clock=clock)


def test_success_is_cached_and_not_stale(breaker):
    cache = {}
    result = recommendations("ana", Primary(["a", "b"]), cache, breaker)
    assert result == {"items": ["a", "b"], "stale": False, "source": "primary"}
    assert cache == {"ana": ["a", "b"]}, "Remember the last good answer per user."


def test_the_timeout_is_passed_to_the_primary(breaker):
    primary = Primary(["a"])
    recommendations("ana", primary, {}, breaker, timeout=0.2)
    assert primary.timeouts == [0.2], "Call primary(user, timeout=timeout) so that the dependency can give up in time."


def test_failure_with_a_cache_serves_the_last_good_list_marked_stale(breaker):
    cache = {}
    recommendations("ana", Primary(["a", "b"]), cache, breaker)
    result = recommendations("ana", Primary(TimeoutError("slow")), cache, breaker)
    assert result == {"items": ["a", "b"], "stale": True, "source": "cache"}, f"Got {result}"


def test_failure_without_a_cache_serves_the_popular_list(breaker):
    result = recommendations("ben", Primary(ConnectionError("down")), {}, breaker)
    assert result == {"items": list(POPULAR), "stale": True, "source": "popular"}, f"Got {result}"


def test_a_custom_popular_list(breaker):
    result = recommendations("ben", Primary(ConnectionError("down")), {}, breaker, popular=("x", "y"))
    assert result["items"] == ["x", "y"] and result["source"] == "popular"


@pytest.mark.parametrize("error", [TimeoutError("t"), ConnectionError("c"), KeyError("k"), ValueError("v"), RuntimeError("r")])
def test_it_never_raises_to_the_page(breaker, error):
    result = recommendations("ana", Primary(error), {}, breaker)
    assert result["stale"] is True, f"A {type(error).__name__} from the dependency must become a fallback, not an exception."


def test_base_exceptions_are_not_swallowed(breaker):
    with pytest.raises(KeyboardInterrupt):
        recommendations("ana", Primary(KeyboardInterrupt()), {}, breaker)


def test_an_empty_answer_is_a_success(breaker):
    cache = {"ana": ["old"]}
    result = recommendations("ana", Primary([]), cache, breaker)
    assert result == {"items": [], "stale": False, "source": "primary"}, "An empty list means 'nothing for you': it is a real answer, not a failure."
    assert cache["ana"] == [], "...and it replaces the old cached list."


def test_the_cache_is_per_user(breaker):
    cache = {}
    recommendations("ana", Primary(["a"]), cache, breaker)
    result = recommendations("ben", Primary(TimeoutError()), cache, breaker)
    assert result["source"] == "popular", "Ben must not get Ana's list."


def test_the_circuit_opens_and_the_primary_is_left_alone(breaker):
    primary = Primary(TimeoutError("down"))
    results = [recommendations("ana", primary, {}, breaker) for _ in range(6)]
    assert primary.calls == 3, f"After 3 failures the circuit is open: calls 4 to 6 must not reach the primary (it was called {primary.calls} times)."
    assert all(r["source"] == "popular" and r["stale"] for r in results), "Every one of the six requests still got an answer."


def test_after_the_pause_one_probe_is_tried_and_recovery_works(breaker, clock):
    cache = {}
    recommendations("ana", Primary(["a"]), cache, breaker)
    down = Primary(TimeoutError("down"))
    for _ in range(3):
        recommendations("ana", down, cache, breaker)
    clock.now = 20.0                                             # reset_after has passed
    back = Primary(["fresh"])
    result = recommendations("ana", back, cache, breaker)
    assert result == {"items": ["fresh"], "stale": False, "source": "primary"}, "The probe succeeds: the circuit closes and fresh data is served again."
    assert back.calls == 1 and breaker.state == "closed"


def test_results_are_copies(breaker):
    cache = {}
    first = recommendations("ana", Primary(["a", "b"]), cache, breaker)
    first["items"].append("hacked")
    assert cache["ana"] == ["a", "b"], "A caller changing the result must not change the cache."
    fallback = recommendations("zoe", Primary(TimeoutError()), {}, breaker)
    fallback["items"].append("hacked")
    assert list(POPULAR) == ["Python tips", "Testing basics", "Docker intro"] and recommendations("kim", Primary(TimeoutError()), {}, breaker)["items"] == list(POPULAR)
