## Walkthrough

| test | A `- 29` | B `extra // 60` | C no cap | D no negative check | E `<= 31` |
|---|---|---|---|---|---|
| free_half_hour `fee(30)` = 0 | ok | ok | ok | ok | ok |
| zero_minutes `fee(0)` = 0 | ok | ok | ok | ok | ok |
| just_over `fee(31)` = 10 | ok (gives 10) | **fails** (extra 1 // 60 = 0 gives 0) | ok | ok | **fails** (gives 0) |
| exact_hour `fee(90)` = 10 | **fails** (61 started minutes make 2 hours: 20) | ok (60 // 60 = 1) | ok | ok | ok |
| next_started_hour `fee(91)` = 20 | ok | **fails** (61 // 60 = 1 gives 10) | ok | ok | ok |
| daily_cap `fee(1440)` = 100 | ok | ok (23 hours still above the cap) | **fails** (gives 240) | ok | ok |
| negative `fee(-5)` raises | ok | ok | ok | **fails** (returns 0, nothing raised) | ok |

Version A shifts the free time by one minute. It gives the same answers for 31 and 91 and is caught only by 90, the border between one started hour and two. Version E is caught only by 31, the first chargeable minute. Every bug is caught by a different test, and no test is caught by all: that is a good suite.

## The exact output

```text
version A: test_exact_hour_after_free_time
version B: test_just_over_free_time, test_next_started_hour
version C: test_daily_cap
version D: test_negative_time
version E: test_just_over_free_time
version F: all pass
```
