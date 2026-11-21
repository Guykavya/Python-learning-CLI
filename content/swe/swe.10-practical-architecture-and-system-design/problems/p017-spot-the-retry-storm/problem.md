# Spot the retry storm

Chapter section 12.2 (retries, backoff and jitter), 12.1 (timeouts) and "Try it: spot the retry storm". Many failures are brief, and a retry often succeeds. But **retries multiply**: if service A retries 3 times calling B, and B retries 3 times calling C, then one user action can become 3 x 3 = 9 calls to C; with three layers, 27. During an outage this **retry storm** crushes the dependency that is trying to recover. The cure is to retry at **one** layer, and to give the whole request a **time budget** (a deadline) that every layer respects.

The program models a request that goes `A -> B -> C -> database`. `attempts[i]` is how many times layer `i` tries the layer below it. The database is overloaded: every call to it **times out after 1 second and fails**, so every attempt at every layer fails. Four configurations are run.

```python
def run(attempts, deadline=None):
    """A request goes A -> B -> C -> database. attempts[i] is how many times layer i tries the layer below it.
    The database is overloaded: every call to it times out after 1 second and fails.
    With a deadline (seconds for the whole request), a layer stops trying once the clock has reached it."""
    state = {"db_calls": 0, "clock": 0.0}

    def call(level):
        if level == len(attempts):                      # the database
            state["db_calls"] += 1
            state["clock"] += 1.0
            return False
        for _ in range(attempts[level]):
            if deadline is not None and state["clock"] >= deadline:
                return False                            # out of budget: stop retrying
            if call(level + 1):
                return True
        return False

    call(0)
    return state["db_calls"], state["clock"]


CASES = [
    ("every layer retries 3 times", [3, 3, 3], None),
    ("retries only at the edge", [3, 1, 1], None),
    ("A and B retry, C does not", [3, 3, 1], None),
    ("every layer retries, 10 s budget", [3, 3, 3], 10),
]
for label, attempts, deadline in CASES:
    calls, seconds = run(attempts, deadline)
    print(f"{label:34} database calls = {calls:2}, time spent = {seconds:4.1f} s")
```

Python facts: `{calls:2}` right-aligns an integer in 2 characters, `{seconds:4.1f}` prints a float with one decimal in 4 characters, `{label:34}` pads the text to 34 characters on the right. The `for _ in range(attempts[level])` loop makes the calls of one layer; `call(level + 1)` is the layer below.

## What to write

The exact output: four lines. Work out the number of calls that reach the database by multiplying the attempts, and think carefully about what the **deadline** does in the last case.

## Example

With `attempts = [1, 1, 1]` (nobody retries) the database is called once and the time spent is 1.0 s.

## After you answer

- In the first configuration, how many calls does the database get for **one** user action? What happens to that number if 1,000 users act at once, and what does an overloaded database do with 27,000 calls?
- Which of the four configurations would you ship, and what else belongs next to it (jitter, a circuit breaker)?
