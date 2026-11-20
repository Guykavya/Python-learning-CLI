# `robots.txt` and a polite rate limiter

Chapter section 24. Write three things.

```python
allowed(robots_text, agent, url)       # -> bool
crawl_delay(robots_text, agent)        # -> float or None
class RateLimiter:
    def __init__(self, min_interval, clock, sleep): ...
    def wait(self): ...
```

**`allowed`**: may the crawler named `agent` fetch `url`, according to the text of a `robots.txt` file? Use `urllib.robotparser.RobotFileParser` and feed it the **text** with `parse(...)` (no network access). An empty file allows everything. The rules of the group for the most specific `User-agent` apply; `*` is the default group.

**`crawl_delay`**: the `Crawl-delay` (seconds, as a float) that applies to `agent`, or `None` if there is none. (The standard-library parser understands whole numbers only: `Crawl-delay: 2` works, `Crawl-delay: 0.5` is ignored and gives `None`.)

**`RateLimiter`**: allows at most one request every `min_interval` seconds. `wait()` is called before every request. The first call returns at once. Later calls sleep for the **remaining** time only: `min_interval - (time since the previous request started)`; if enough time has already passed they do not sleep. `clock()` returns the current time and `sleep(seconds)` waits; both are **parameters**, so tests use a fake clock and never really wait. After sleeping, read the clock again and remember that as the time of this request.

## Example

```python
ROBOTS = "User-agent: *\nDisallow: /private/\nCrawl-delay: 2\n"
allowed(ROBOTS, "mybot", "http://shop.test/tea")            # True
allowed(ROBOTS, "mybot", "http://shop.test/private/x")      # False
crawl_delay(ROBOTS, "mybot")                                 # 2.0
```
