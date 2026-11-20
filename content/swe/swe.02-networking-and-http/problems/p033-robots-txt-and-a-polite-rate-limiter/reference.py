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
