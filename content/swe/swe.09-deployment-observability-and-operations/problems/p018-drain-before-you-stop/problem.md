# Drain before you stop

Chapter section 9.5 (graceful shutdown: finish what you started), 2.6 (signals) and the `lifespan` function of 5.1. When the platform stops a container it sends `SIGTERM`. A good service (1) turns **readiness red** so no new requests are sent, (2) lets the requests **already in flight** finish, (3) closes its connections, (4) exits before the kill timeout. Write the bookkeeping for steps 1 and 2.

No test sends a real signal: the signal handler is just a function you call.

## What to write

```python
class Lifecycle:
    def __init__(self, clock=time.monotonic, sleep=time.sleep): ...
    draining: bool            # property, False at the start
    in_flight: int            # property: requests being handled right now
    def on_sigterm(self): ...                 # start draining
    def track(self): ...                      # a context manager around one request
    def readiness(self) -> tuple[int, dict]: ...
    def wait_idle(self, timeout: float, poll: float = 0.1) -> bool: ...
```

- `on_sigterm()` sets `draining` to `True` (calling it twice is harmless).
- `track()` is used as `with lifecycle.track(): handle_request()`. It adds 1 to `in_flight` when the block starts and subtracts 1 when it ends, **also when the block raises**. It must be **thread-safe** (use a `threading.Lock`): many requests are handled at the same time. A request that arrives **while draining is still served**: `track()` never refuses (the load balancer needs a moment to stop sending traffic).
- `readiness()` returns `(200, {"status": "ready"})`, or while draining `(503, {"status": "not ready", "problems": {"draining": "shutting down"}})`.
- `wait_idle(timeout, poll)` waits until `in_flight` is 0 and returns `True`; if `timeout` seconds pass first it returns `False`. It must use the **injected** `clock()` and `sleep()` (the tests use a fake clock, so nothing really sleeps): loop `while in_flight > 0`, and sleep `min(poll, remaining time)` so that the total never exceeds `timeout`. With nothing in flight it returns `True` at once, without sleeping.

## Example

```python
lc = Lifecycle()
with lc.track():
    lc.in_flight                 # 1
lc.in_flight                     # 0
lc.on_sigterm()
lc.readiness()                   # (503, {'status': 'not ready', 'problems': {'draining': 'shutting down'}})
lc.wait_idle(timeout=30)         # True once the last request finished, False if one is still running after 30 s
```

In the real service `on_sigterm` is called from the `lifespan` shutdown, `/readyz` returns `lifecycle.readiness()`, and after `wait_idle` the process exits. If `wait_idle` returns `False`, the platform's `SIGKILL` is about to arrive: log what was still running.
