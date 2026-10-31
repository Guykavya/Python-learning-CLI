- **Grouping but still sorting inside the loop** (`result[day] = sorted(by_day[day])[:k]` for every
  event). The scan is gone, but on a busy day the sort is repeated for every event. Sort after the
  loop.
- **Building the days with `if day not in days_list`.** That is another list scan per event.
- **Sorting the days.** The result must keep first-seen order; a dict does that by itself.
- **Using `set` for the scores.** Equal scores must all be kept.
- **Forgetting `k = 0`.** `heapq.nlargest(0, ...)` and `[:0]` both give `[]`, but a day must still
  be in the result.
- **Timing a single tiny input to "prove" it is faster.** On 6 events both take microseconds; the
  difference shows on thousands.
