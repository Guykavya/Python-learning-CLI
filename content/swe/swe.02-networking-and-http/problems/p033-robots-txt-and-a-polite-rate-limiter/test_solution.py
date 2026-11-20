import pytest

from solution import RateLimiter, allowed, crawl_delay

ROBOTS = """
User-agent: *
Disallow: /private/
Disallow: /search
Crawl-delay: 2

User-agent: badbot
Disallow: /

User-agent: goodbot
Allow: /private/public/
Disallow: /private/
Crawl-delay: 1
""".strip()

SITE = "http://shop.test"


def test_the_default_group():
    assert allowed(ROBOTS, "mybot", SITE + "/tea/green") is True
    assert allowed(ROBOTS, "mybot", SITE + "/private/orders") is False
    assert allowed(ROBOTS, "mybot", SITE + "/search?q=tea") is False, "'Disallow: /search' blocks every URL that starts with it."


def test_a_group_for_one_agent():
    assert allowed(ROBOTS, "badbot", SITE + "/tea") is False, "badbot is disallowed everywhere."
    assert allowed(ROBOTS, "goodbot", SITE + "/search") is True, "The goodbot group has no rule for /search; the * group does not apply to it."
    assert allowed(ROBOTS, "goodbot", SITE + "/private/public/x") is True
    assert allowed(ROBOTS, "goodbot", SITE + "/private/y") is False


def test_empty_robots_allows_everything():
    assert allowed("", "bot", SITE + "/anything") is True
    assert allowed("# just a comment\n", "bot", SITE + "/anything") is True


def test_crawl_delay():
    assert crawl_delay(ROBOTS, "mybot") == 2.0 and isinstance(crawl_delay(ROBOTS, "mybot"), float)
    assert crawl_delay(ROBOTS, "goodbot") == 1.0
    assert crawl_delay(ROBOTS, "badbot") is None
    assert crawl_delay("User-agent: *\nDisallow: /x\n", "bot") is None


class Fake:
    def __init__(self):
        self.now = 0.0
        self.waits = []

    def clock(self):
        return self.now

    def sleep(self, s):
        self.waits.append(round(s, 6))
        self.now += s


def test_first_call_does_not_wait():
    f = Fake()
    lim = RateLimiter(2.0, f.clock, f.sleep)
    lim.wait()
    assert f.waits == [], "The very first request needs no pause."


def test_the_chapter_scenario_waits_only_for_the_rest():
    f = Fake()
    lim = RateLimiter(2.0, f.clock, f.sleep)
    for work in (0.0, 0.5, 5.0):
        lim.wait()
        f.now += work
    assert f.waits == [2.0, 1.5], f"Waits should be [2.0, 1.5], got {f.waits}: sleep only the remaining time."


def test_no_wait_when_enough_time_has_passed():
    f = Fake()
    lim = RateLimiter(2.0, f.clock, f.sleep)
    lim.wait()
    f.now += 3
    lim.wait()
    assert f.waits == [], "3 s have passed since the last request: no pause."
    f.now += 2
    lim.wait()
    assert f.waits == [], "Exactly 2 s passed: no pause (and never sleep(0) or a negative value)."


def test_requests_are_spaced_at_least_the_interval_apart():
    f = Fake()
    lim = RateLimiter(1.5, f.clock, f.sleep)
    starts = []
    for work in (0.2, 0.0, 1.0, 0.3, 0.0):
        lim.wait()
        starts.append(f.now)
        f.now += work
    gaps = [b - a for a, b in zip(starts, starts[1:])]
    assert all(g >= 1.5 - 1e-9 for g in gaps), f"Gaps between request starts must be >= 1.5 s, got {gaps}."


def test_the_next_gap_counts_from_the_wake_up_time():
    f = Fake()
    real_sleep = f.sleep

    def late_sleep(s):          # the operating system wakes us 0.3 s late
        real_sleep(s + 0.3)

    lim = RateLimiter(2.0, f.clock, late_sleep)
    lim.wait()
    lim.wait()
    start2 = f.now
    lim.wait()
    assert f.now - start2 == pytest.approx(2.3), "Read the clock again after sleeping: the request really starts then."
