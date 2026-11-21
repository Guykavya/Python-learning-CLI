## Hint 1

Fan-out on write writes **one row per follower per post**: for each account multiply `posts` by `followers`, then add. A day has 86,400 seconds. For the read side, first compute how many feed opens happen per second (`READERS_PER_DAY * FEED_OPENS_PER_READER / SECONDS_PER_DAY`), then how many accounts each open must look at.

## Hint 2

Work the lines in order. Line 1 is a sum of three products. Line 2 divides line 1 by 86,400 and rounds. Line 3 multiplies the feed opens per second by 100 accounts per open and rounds. Line 4 is the same sum as line 1 but only for accounts whose followers are **at most** the threshold. Line 5 lists the accounts above the threshold, sorted.

```text
10 x 200 + 4 x 50 + 5 x 1_000_000 = ?        / 86_400 = ?
2_000_000 x 20 / 86_400 x 100 = ?
accounts with followers <= 10_000: ana, ben;  above: star
```
