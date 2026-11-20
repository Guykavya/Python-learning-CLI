## Approach

```python
from urllib.robotparser import RobotFileParser


def _parser(robots_text):
    rp = RobotFileParser()
    rp.parse(robots_text.splitlines())
    return rp


def allowed(robots_text, agent, url):
    return _parser(robots_text).can_fetch(agent, url)


def crawl_delay(robots_text, agent):
    delay = _parser(robots_text).crawl_delay(agent)
    return None if delay is None else float(delay)


class RateLimiter:
    def __init__(self, min_interval, clock, sleep):
        self.min_interval = min_interval
        self.clock = clock
        self.sleep = sleep
        self.last = None

    def wait(self):
        now = self.clock()
        if self.last is not None:
            remaining = self.min_interval - (now - self.last)
            if remaining > 0:
                self.sleep(remaining)
                now = self.clock()
        self.last = now
```

`RobotFileParser` implements the matching rules (groups per agent, `Allow` and `Disallow` with the longest match winning), so we only feed it text. The limiter sleeps for the **remaining** time, not a fixed pause: if your own processing between two requests already took 1.5 s of a 2 s interval, you wait only 0.5 s. Reading the clock again after the sleep records the real start of this request, so a late wake-up does not make the next gap too short.

Example (interval 2.0, work of 0, 0.5 and 5 s between requests): the first call does not wait; the second waits the full 2.0 s; the third waits 1.5 s (0.5 s were used); a fourth call after the 5-second job would not wait at all.

## Complexity

`O(1)` per `wait`; parsing is `O(lines)`.

## Another way

A token bucket allows short bursts and a long-term average rate; the "minimum interval" limiter is the simplest and the politest.

## Why it matters

Scrapers that ignore `robots.txt` and hammer a site get blocked, and may harm a small server. Checking the rules and spacing requests is part of the job (chapter section 24.1).
