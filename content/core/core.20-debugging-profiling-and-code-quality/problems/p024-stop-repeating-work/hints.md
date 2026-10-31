## Hint 1

What does the loop compute for the 2nd, 3rd, ... event of the same day that it did not already
compute for the 1st? Could you first collect each day's scores (one pass), and only **then**
sort?

## Hint 2

Group in one pass with a dictionary of lists (it keeps the days in first-seen order), then sort
each group once.

```
by_day = {}
for day, score in events:
    by_day.setdefault(day, []).append(score)
return {day: sorted(scores, reverse=True)[:k] for day, scores in by_day.items()}
```

Do not keep `sorted(...)` inside the first loop: sorting a growing list for every event is still
repeated work.
