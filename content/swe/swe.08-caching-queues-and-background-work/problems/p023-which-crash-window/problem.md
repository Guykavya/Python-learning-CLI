# Which crash window?

Chapter sections 11.2 (the crash windows), 11.4 (the e-mail worker, the wrong way) and "Try it: which window?". Below is a small, complete model of a queue with **at-least-once** delivery and the **naive** e-mail handler (no key, no record). A job is acknowledged only after the handler returns. A crash kills the worker; then a second worker takes every job that was not acknowledged.

```python
class Crash(BaseException):
    """The process dies. `except Exception` does not catch it."""


def run(crash_at=None, jobs=1, lose_response=False):
    outbox = []                                       # e-mails the customer really received
    pending = [{"id": n, "to": "ada"} for n in range(1, jobs + 1)]   # jobs not yet acknowledged
    state = {"crash_at": crash_at, "lose": lose_response}

    def hit(point):
        if state["crash_at"] == point:
            state["crash_at"] = None                  # crash only once
            raise Crash(point)

    def send(to):
        outbox.append(to)                             # the provider sends...
        if state["lose"]:
            state["lose"] = False
            raise TimeoutError("response lost")       # ...but the answer never arrives

    def naive_handler(job):                           # no key, no record
        hit("start")
        hit("before-send")
        send(job["to"])
        hit("after-send")
        hit("end")

    for worker in ("worker-1", "worker-2"):           # worker-2 starts after worker-1 is gone
        for job in list(pending):
            try:
                naive_handler(job)
            except Crash:
                break                                 # the process died: it acks nothing more
            except Exception:
                continue                              # an ordinary error: not acked, retried later
            pending.remove(job)                       # ack
    return len(outbox), len(pending)


print("1:", run("start"))
print("2:", run("before-send"))
print("3:", run("after-send"))
print("4:", run("end"))
print("5:", run(lose_response=True))
print("6:", run(jobs=2))
print("7:", run("after-send", jobs=2))
```

Python facts: `print("1:", (1, 0))` prints `1: (1, 0)`. `for job in list(pending)` loops over a **copy**, so removing from `pending` inside the loop is safe. `break` leaves the inner loop only; worker-2 still runs.

## What to write

The exact seven lines of output.

## Example

Line 1: the crash happens at `"start"`, before anything is sent. Worker-2 runs the job: one e-mail, and the job is acknowledged. `1: (1, 0)`.

## After you answer

- Which crash points are inside the window where the effect is done but the ack is not?
- Line 7 sends three e-mails for one welcome message. Which two defences of problem p022 would bring every line to `(1, 0)`?
