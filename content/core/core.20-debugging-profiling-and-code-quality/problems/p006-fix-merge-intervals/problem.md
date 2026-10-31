# Fix: the interval merger that lies

`starter.py` holds `merge_intervals`, used by a room-booking tool to turn a list of booked time
ranges into "busy" blocks. An interval is a pair `[start, end]` with `start <= end`. Two
intervals that **overlap or touch** (`[1, 3]` and `[3, 5]`) become one (`[1, 5]`). The result
is sorted by start, and it is a **new** list of **new** `[start, end]` lists: the caller's data
must not change.

It passed the one example its author tried, `[[1, 3], [2, 6], [8, 10]]`. Then the bug reports
came in:

- "The 9:00 to 10:00 and 10:00 to 11:00 meetings show up as two separate busy blocks."
- "A full-day booking `[9, 17]` with a short meeting `[10, 11]` inside it shows the room
  busy only from 9 to 11."
- "After I call it, **my own** list of bookings has been re-ordered, and one of my bookings
  now has a different end time."
- "With no bookings at all it crashes with `IndexError`."
- "Bookings stored as tuples, like `[(1, 2), (2, 4)]`, crash with `TypeError`."

Copy `starter.py` to `solution.py` and fix `merge_intervals(intervals)`. Keep the name and
the parameter.

This is a debugging exercise, so work like a debugger: for each report, write the smallest
input that shows it, put a `breakpoint()` (or a `print`) inside the loop, and watch `last`,
`merged` and the caller's list change. Some reports share a cause, and one fix may cause
another report to come back. Check them all.

**Example**

```python
bookings = [[8, 10], [1, 3], [2, 6]]
merge_intervals(bookings)      # [[1, 6], [8, 10]]
bookings                       # [[8, 10], [1, 3], [2, 6]]   (unchanged)

merge_intervals([[1, 3], [3, 5]])      # [[1, 5]]
merge_intervals([[9, 17], [10, 11]])   # [[9, 17]]
merge_intervals([])                    # []
merge_intervals([(1, 2), (2, 4)])      # [[1, 4]]
```
