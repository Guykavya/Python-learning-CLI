# Meeting rooms II

You get a list of meetings, each a pair `(start, end)` of whole numbers with `start < end`. Two meetings **overlap** if they are on at the same moment. A meeting that **ends** at time `t` and a meeting that **starts** at time `t` do **not** overlap: the room is free again at `t`.

Write `min_rooms(intervals)`, which returns the smallest number of rooms that can hold all meetings (every meeting stays in one room, from its start to its end). With no meetings the answer is `0`. Do not change the input list.

## Example

```python
>>> min_rooms([(0, 30), (5, 10), (15, 20)])
2
>>> min_rooms([(7, 10), (2, 4)])
1
>>> min_rooms([(1, 5), (5, 9)])
1
>>> min_rooms([])
0
```

In the first example the meeting `(0, 30)` runs the whole time, and `(5, 10)` and `(15, 20)` can share a second room. In the third example the first meeting ends at `5` and the second starts at `5`: one room is enough.

## Constraints

- Up to 100,000 meetings; times are integers up to 10**9. The input is not sorted.
- The big tests run in a separate process with a 10-second limit. Comparing every meeting with every other (`O(n^2)`) does not finish in time.

## Think about

Walk through the meetings in the order of their start times. You need to know, at each start, whether **some** room is free: and which room frees up **first**. Which single number per room must you remember, and which structure gives you the smallest of them again and again?
