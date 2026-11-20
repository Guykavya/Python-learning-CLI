from urllib.robotparser import RobotFileParser


def allowed(robots_text, agent, url):
    # TODO: RobotFileParser().parse(lines), then can_fetch
    return True


def crawl_delay(robots_text, agent):
    return None


class RateLimiter:
    def __init__(self, min_interval, clock, sleep):
        self.min_interval = min_interval
        self.clock = clock
        self.sleep = sleep
        self.last = None

    def wait(self):
        # TODO: sleep only for the REMAINING time since the previous request
        pass
