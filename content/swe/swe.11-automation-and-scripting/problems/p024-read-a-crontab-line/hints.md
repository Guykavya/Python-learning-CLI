## Hint 1

Read each field as a filter, and a time runs only when **all** five pass. `*/15` in the minute field means minutes 0, 15, 30, 45. `1-5` in the day-of-week field means Monday to Friday, so a Friday-night start skips the weekend. `1` in the day-of-month field means only the first day of each month. The next run must be strictly **after** 23:50.

## Hint 2

Line 1: after 23:50 the next quarter-hour is midnight, which is already Saturday. Line 2: Saturday and Sunday fail the weekday filter. Line 3: the next "first of the month" after 20 November is 1 December. For line 5, look at the table in section 12.2: which character means something special to cron itself, before the shell even sees the command?
