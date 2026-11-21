## Approach

| Quantity | Calculation | Result |
|---|---|---|
| inbox rows per day, fan-out on write | 10 x 200 + 4 x 50 + 5 x 1,000,000 = 2,000 + 200 + 5,000,000 | **5,002,200** |
| inbox rows per second | 5,002,200 / 86,400 = 57.9 | **58** |
| feed opens per second | 2,000,000 x 20 / 86,400 = 462.96 | (intermediate) |
| source lookups per second, fan-out on read | 462.96 x 100 | **46,296** |
| inbox rows per day, hybrid (threshold 10,000) | only `ana` and `ben` are fanned out: 2,000 + 200 | **2,200** |
| merged at read time | accounts above the threshold | `['star']` |

The chapter's conclusions: fan-out on write makes **reads trivial and writes expensive** (one account with a million followers causes 5 million inbox rows a day, 99.96% of the total); fan-out on read keeps writes at one row per post but makes every read touch many sources (46,296 lookups per second here). The **hybrid** takes the best of both: ordinary accounts are pushed (cheap, because few followers), the one huge account is merged at read time (a little more work at read time, only for the few readers who follow it), and the write cost stays small. The threshold is a number you **choose from measurements**. If every account has fewer than about 100 followers, plain fan-out on read is simpler and fast enough: stop there.

## Cost

Reading only. Rerun the program with a different `THRESHOLD` (1,000, 100) and watch the hybrid's rows per day and the list of accounts merged at read time change.

## Another way

The chapter measures both strategies on SQLite for 30-member projects (599,352 extra rows for 20,000 events, write time 24 ms versus 572 ms, reads 0.013 ms versus 0.009 ms). The lesson there is the opposite one: at small fan-out, the extra rows buy nothing you can feel.
