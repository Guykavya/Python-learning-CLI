# Platforms needed

A railway station has a timetable for one day. Train `i` arrives at `arrivals[i]` and leaves at `departures[i]` (times like `950` for 9:50). Write `min_platforms(arrivals, departures)`: the fewest platforms so that no train ever waits for one.

Rules:

- Both lists have the same length, `arrivals[i] < departures[i]` for every train, and the lists are **not** sorted (`departures[i]` belongs to the same train as `arrivals[i]`).
- **Same-time rule (chapter section 6):** when one train leaves at the exact minute another arrives, the leaving train is gone first, so the arriving train **can use that platform**. A departure at `t` frees a platform for an arrival at `t`.
- Return an `int`. No trains need `0` platforms. Do not change the lists you are given.

## Example

```python
>>> min_platforms([900, 940, 950, 1100, 1500, 1800], [910, 1200, 1120, 1130, 1900, 2000])
3
>>> min_platforms([900, 1000], [1000, 1100])        # one leaves at 1000, one arrives at 1000
1
>>> min_platforms([], [])
0
```

In the first example the peak is at 1100: the trains that arrived at 940 and 950 are still there, and a third one arrives.

## Constraints

- `0 <= n <= 10**5`. Aim for `O(n log n)` with the two-pointer walk of the chapter (sort arrivals and departures **separately**).

## Think about

Why may you sort the two lists separately and "forget" which departure belongs to which train? In the two-pointer walk, which comparison (`<` or `<=`) puts the departure first when the times are equal?
