# Stop repeating work

A game server keeps a leaderboard of the best scores of each day:

```python
def top_k_each_day(events, k):
    result = {}
    for day, score in events:
        scores = sorted([s for d, s in events if d == day], reverse=True)
        result[day] = scores[:k]
    return result
```

It gives the right answer, but for **every single event** it walks through **all** events again
and sorts that day's scores again, even though it already did exactly that for the previous
event of the same day. With 2,000 events it does about 4 million steps for a job that needs a few
thousand.

Rewrite `top_k_each_day(events, k)` in `solution.py` (the starter is the slow version) so each
event is looked at a constant number of times and each day is sorted **once**. The result must
be identical:

- a dictionary `{day: list of the k highest scores of that day, highest first}`;
- days in the order they **first appear** in `events`;
- if a day has fewer than `k` scores, all of them; `k = 0` gives an empty list for every day;
- equal scores are all kept (`[9, 9, 4]`, not `[9, 4]`).

**How speed is graded.** No fixed time limit. The tests time the original version and yours on
the same machine, in the same run, and expect yours to be **at least 5 times faster** (a good
solution is a few hundred times faster).

**Example**

```python
events = [("mon", 5), ("tue", 7), ("mon", 9), ("mon", 1), ("tue", 7), ("mon", 9)]
top_k_each_day(events, 2)
# {'mon': [9, 9], 'tue': [7, 7]}
top_k_each_day(events, 0)
# {'mon': [], 'tue': []}
```
