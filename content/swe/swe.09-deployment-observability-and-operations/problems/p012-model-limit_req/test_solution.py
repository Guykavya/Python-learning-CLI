import pytest

from solution import LimitReq


def run(times, **kwargs):
    lim = LimitReq(**kwargs)
    return [lim.allow(t) for t in times]


def test_the_example_without_nodelay():
    assert run([0, 0, 0, 0, 1, 1, 3], rate_per_s=1, burst=2) == ["pass", "delayed", "delayed", "503", "delayed", "503", "delayed"], \
        "rate 1/s, burst 2: the bucket fills to 2 then refuses; it drains by 1 per second."


def test_the_example_with_nodelay():
    assert run([0, 0, 0, 0, 1, 1, 3], rate_per_s=1, burst=2, nodelay=True) == ["pass", "pass", "pass", "503", "pass", "503", "pass"], \
        "nodelay: the burst requests pass at once instead of being delayed; the refusals are the same."


def test_no_burst_means_strict_spacing():
    assert run([0, 0, 0.5, 1, 1, 2], rate_per_s=1, burst=0) == ["pass", "503", "503", "pass", "503", "pass"], \
        "burst=0: a request is accepted only if at least 1/rate seconds have passed since the last accepted one."


def test_exactly_at_the_rate_always_passes():
    assert run([0, 0.5, 1, 1.5, 2], rate_per_s=2, burst=0) == ["pass"] * 5, "Requests spaced exactly 1/rate apart never exceed the rate."


def test_small_burst_without_nodelay():
    assert run([0, 0, 0, 0.5, 0.5], rate_per_s=2, burst=1) == ["pass", "delayed", "503", "delayed", "503"], \
        "rate 2/s, burst 1: second request delayed, third refused; after 0.5 s the bucket has drained by 1."


def test_bucket_refills_at_the_rate():
    first = run([0, 0, 0, 0, 0, 3, 3, 3, 3], rate_per_s=1, burst=3, nodelay=True)
    assert first == ["pass", "pass", "pass", "pass", "503", "pass", "pass", "pass", "503"], \
        "After 3 idle seconds the bucket has drained by 3, so a new burst of up to 3 more is accepted."


def test_a_long_pause_resets_everything():
    assert run([0, 0, 100, 100], rate_per_s=1, burst=1) == ["pass", "delayed", "pass", "delayed"], \
        "excess never goes below 0: after a long pause the bucket is empty, not 'in credit'."


def test_refused_requests_do_not_fill_the_bucket():
    lim = LimitReq(rate_per_s=1, burst=1)
    assert [lim.allow(0) for _ in range(6)] == ["pass", "delayed", "503", "503", "503", "503"]
    assert lim.allow(1) == "delayed", \
        "The refusals must not change the state: at t=1 the bucket (excess 1) has drained to 0 and the new request makes it 1 again."


def test_time_must_not_go_backwards():
    lim = LimitReq(rate_per_s=1, burst=1)
    lim.allow(5)
    with pytest.raises(ValueError):
        lim.allow(4)


@pytest.mark.parametrize("kwargs", [{"rate_per_s": 0}, {"rate_per_s": -1}, {"rate_per_s": 1, "burst": -1}])
def test_bad_settings(kwargs):
    with pytest.raises(ValueError):
        LimitReq(**kwargs)


def test_chapter_numbers():
    lim = LimitReq(rate_per_s=20, burst=40, nodelay=True)
    answers = [lim.allow(0.0) for _ in range(60)]
    assert answers.count("pass") == 41 and answers.count("503") == 19, \
        "At the same instant: the first request plus a burst of 40 pass (41 in all); the other 19 of 60 are refused."
