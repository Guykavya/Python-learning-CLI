# Trace activity selection

The earliest-finish greedy of chapter section 4, with a print on every step. Predict **exactly** what this program prints. Do not run it.

```python
events = [(5, 9), (1, 4), (3, 5), (0, 6), (4, 7), (6, 9), (8, 11), (11, 12)]

order = sorted(events, key=lambda ev: (ev[1], ev[0]))
print("order:", order)

chosen = []
last_end = float("-inf")
for s, e in order:
    if s >= last_end:
        chosen.append((s, e))
        last_end = e
        print(f"({s}, {e}) take  last_end={last_end}")
    else:
        print(f"({s}, {e}) skip  last_end={last_end}")
print("chosen:", len(chosen), chosen)
```

Write your answer in `answer.txt`, one printed line per line: the `order:` line, then one line per event, then the `chosen:` line.

## How to work

1. Sort first, on paper. The key is `(end, start)`: by end time, and when two ends are equal, by start time. Two events here end at the same time.
2. Keep one number, `last_end`, in a box. It starts as `-inf` (that is how Python prints `float("-inf")`).
3. For each event in sorted order: `take` if `start >= last_end` (touching is allowed), and then the box changes **before** the line is printed. On `skip` the box does not change.

## After you answer

1. Which taken event **touches** the previous one (starts exactly at `last_end`)? What would `s > last_end` print instead?
2. `(0, 6)` is skipped. Is it skipped because it is long, or because of its start time?
3. If the key were only `ev[0]` (start time), which event would be taken first, and how many events would be chosen?
