# Build a bounded round-robin scheduler

An operating system runs many jobs on one processor by giving each job a short time slice, the **quantum**, in turn. A job that is not finished after its slice goes to the **back** of the ready queue (chapter section 12, "Round-robin scheduling"). Here the ready queue is also **bounded**: it holds at most `capacity` jobs, and new jobs are rejected while it is full.

Build a class `Scheduler`:

| Member | Behaviour |
|---|---|
| `Scheduler(quantum, capacity)` | `ValueError` if `quantum <= 0` or `capacity <= 0`. The clock starts at 0. |
| `submit(name, work)` | `ValueError` if `work <= 0`. If the ready queue already holds `capacity` jobs, return `False` and change nothing. Otherwise add `(name, work)` at the back and return `True`. |
| `step()` | If the queue is empty, return `None` and do nothing (the clock does not move). Otherwise take the **front** job, run it for `min(quantum, work left)` time units (the clock advances by that much), then: if work is left, put it at the **back** with its remaining work; if not, record `(name, clock)` in `finished`. Return the name of the job that ran. |
| `run_all()` | Call `step()` until the queue is empty; return a copy of `finished` (as a list). |
| `clock` | Attribute: the current time. |
| `finished` | Attribute: a list of `(name, finish_time)` tuples in the order the jobs finished. |
| `len(s)` | The number of jobs in the ready queue. |

A job that goes back after its slice is **not** a new submission: it is never rejected. (It just left the queue, so there is always room for it.)

## Example

```python
>>> s = Scheduler(quantum=2, capacity=3)
>>> [s.submit("A", 5), s.submit("B", 3), s.submit("C", 1), s.submit("D", 2)]
[True, True, True, False]
>>> s.run_all()
[('C', 5), ('B', 8), ('A', 9)]
>>> s.clock
9
```

`A` runs 2 (clock 2, 3 left, to the back), `B` runs 2 (clock 4, 1 left), `C` runs 1 and finishes at 5, `A` runs 2 (clock 7, 1 left), `B` runs 1 and finishes at 8, `A` runs 1 and finishes at 9. `D` was rejected because three jobs were waiting.

## How it is tested

The tests run several scripted sessions (submits and steps mixed) and compare the **exact** finish order and finish times, the clock, the return values of `submit` and `step`, and `len`. The expected values were traced by hand and confirmed by running a reference solution. Use a `deque` for the ready queue.

## Think about

Why can a job never be rejected when it returns to the back of the queue after its slice? Which simple rule decides the finish order when the quantum is larger than every job?
