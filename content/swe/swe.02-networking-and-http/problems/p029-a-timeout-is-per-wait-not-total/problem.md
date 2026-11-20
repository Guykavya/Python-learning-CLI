# A timeout is per wait, not total

Chapter section 20.3. A server sends a 10-byte answer, **one byte at a time**: byte `i` arrives at `0.8 * i` seconds (so the last byte arrives at 8.0 seconds). The client has a **read timeout**: it gives up if it waits longer than the timeout for the *next* byte. Some clients also have a **total deadline**.

The program below simulates this. All times are in **tenths of a second** inside the code; the printed times are in seconds.

```python
arrivals = [8 * i for i in range(1, 11)]       # byte i arrives at 0.8 * i seconds

def per_wait(timeout):                          # only a read timeout (longest wait for ONE byte)
    clock = 0
    for got, t in enumerate(arrivals):
        if t - clock > timeout:
            return f"timeout after {(clock + timeout) / 10:.1f}s with {got} bytes"
        clock = t
    return f"done at {clock / 10:.1f}s with {len(arrivals)} bytes"

def with_deadline(timeout, total):             # read timeout AND a deadline for the whole answer
    clock = 0
    for got, t in enumerate(arrivals):
        wait = min(timeout, total - clock)
        if t - clock > wait:
            return f"timeout after {(clock + wait) / 10:.1f}s with {got} bytes"
        clock = t
    return f"done at {clock / 10:.1f}s with {len(arrivals)} bytes"

print("read timeout 1.0 s:", per_wait(10))
print("read timeout 0.5 s:", per_wait(5))
print("timeout 1.0 s, deadline 3.0 s:", with_deadline(10, 30))
print("timeout 1.0 s, deadline 10.0 s:", with_deadline(10, 100))
```

Predict **exactly** the four lines that are printed. Do not run it.

Write your answer in `answer.txt`.

## How to work

1. `t - clock` is how long the client has been waiting for the next byte (`clock` is the time of the last byte; at the start it is 0).
2. In `per_wait`, the client fails only if one single gap is longer than `timeout`. The gaps here are all 0.8 s.
3. In `with_deadline`, the time left shrinks: `wait = min(timeout, total - clock)`.

## After you answer

1. Why does a read timeout of 1.0 s never fire although the answer takes 8.0 seconds?
2. Which of the four settings protects you against a server that is slow but never stops?
3. What should a real client use if it needs "the whole answer within 3 seconds"?
