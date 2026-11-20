## Approach

| # | Expression | Reasoning | Next run |
|---|---|---|---|
| 1 | `*/20 * * * *` | minutes 0, 20, 40; after Sat 23:50 the next is midnight | Sun 2026-11-08 00:00 |
| 2 | `0 9 * * 1-5` | weekdays only; Saturday and Sunday are skipped | Mon 2026-11-09 09:00 |
| 3 | `0 0 1 */3 *` | months 1, 4, 7, 10; the next 1st of one of those is 1 January | Fri 2027-01-01 00:00 |
| 4 | `0 12 20 * 1` | both day fields restricted: the 20th **or** a Monday; Monday 9 November comes first | Mon 2026-11-09 12:00 |
| 5 | `30 1 * * *` in London | 01:30 does not exist on 29 March; fold=0 uses GMT: 01:30 UTC, which is 02:30 BST | 01:30 UTC, shown as 02:30 |
| 6 | 01:30 on 25 October | happens twice: BST (00:30 UTC) and then GMT (01:30 UTC) | two different instants |

So a job written as "01:30 London" runs at 02:30 local time on the spring night (or is skipped, depending on the scheduler), and a careless scheduler can run it **twice** on the autumn night, one hour apart.

## Cost

Reading only. The lesson is cheap to apply: schedule technical jobs in **UTC**; use a local zone only when the job must follow the wall clock (a 09:00 digest), and then decide and **test** what the two transition days mean for it.

## Another way

Paste the chapter's `cron.py` into `playground/` and run the program; then change line 5 to `America/New_York` with the chapter's dates (2026-03-08) and predict the result first.
