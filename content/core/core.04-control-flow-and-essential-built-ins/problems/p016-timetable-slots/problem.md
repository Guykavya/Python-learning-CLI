# Timetable slots

A lab is open from a start time to an end time. Bookings are made in fixed-length slots
that start at the opening time, one after another. A slot must **end** no later than the
closing time.

Read three lines: the start time `HH:MM`, the end time `HH:MM` (both on the same day), and
the slot length in minutes. Print every slot as `HH:MM-HH:MM`, one per line, using two
digits for hours and minutes.

- If no slot fits, print `No slots`.
- If the length is 0 or less, print `invalid length`.

**Example**

Input `09:00`, `11:00`, `45`. Output:

```
09:00-09:45
09:45-10:30
```

(A third slot would end at 11:15, after closing.)
