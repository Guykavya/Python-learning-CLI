## Hint 1

`RobotFileParser().parse(lines)` takes a list of lines. Which string method turns a text into lines? Then ask `can_fetch(agent, url)` and `crawl_delay(agent)`.

## Hint 2

For the limiter, keep one number: the time of the last request. On `wait()`, how long ago was it? Compare with `min_interval`: sleep only for the difference, and only if it is positive.

## Hint 3

```text
wait():
    now = clock()
    if last is not None:
        remaining = min_interval - (now - last)
        if remaining > 0: sleep(remaining); now = clock()
    last = now
```
