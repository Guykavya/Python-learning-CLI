# Fan-out on write or on read?

Chapter section 17.2 (the central question: fan-out on write or on read?) and "Try it: one huge project". A feed shows each user what happened in the places they follow. There are two ways to build it:

- **Fan-out on read** ("pull"): store each post **once**. When a user opens their feed, query the posts of all the accounts they follow, merge, sort, take the first 20.
- **Fan-out on write** ("push"): when a post is made, **copy** a pointer into an inbox row for each follower. Reading is then a simple "my inbox, newest first".

Large systems often combine both (**hybrid**): fan out on write for ordinary accounts, but **skip the fan-out for huge accounts** (above a follower threshold) and merge their recent posts into the feed at read time.

The program below puts numbers on the trade-off for three accounts. Each follower reads their feed 20 times a day, and each reader follows 100 accounts.

```python
SECONDS_PER_DAY = 86_400
ACCOUNTS = {                                        # followers and posts per day
    "ana": {"followers": 200, "posts": 10},
    "ben": {"followers": 50, "posts": 4},
    "star": {"followers": 1_000_000, "posts": 5},
}
READERS_PER_DAY = 2_000_000                         # people who open their feed, 20 times a day each
FEED_OPENS_PER_READER = 20
ACCOUNTS_FOLLOWED_PER_READER = 100
THRESHOLD = 10_000                                  # hybrid: accounts above this many followers are not fanned out

rows_per_day = sum(a["posts"] * a["followers"] for a in ACCOUNTS.values())
opens_per_second = READERS_PER_DAY * FEED_OPENS_PER_READER / SECONDS_PER_DAY
hybrid_rows = sum(a["posts"] * a["followers"] for a in ACCOUNTS.values() if a["followers"] <= THRESHOLD)
merged_at_read = sorted(name for name, a in ACCOUNTS.items() if a["followers"] > THRESHOLD)

print(f"fan-out on write: inbox rows written per day     = {rows_per_day}")
print(f"fan-out on write: inbox rows written per second  = {round(rows_per_day / SECONDS_PER_DAY)}")
print(f"fan-out on read : source lookups per second      = {round(opens_per_second * ACCOUNTS_FOLLOWED_PER_READER)}")
print(f"hybrid          : inbox rows written per day     = {hybrid_rows}")
print(f"hybrid          : merged at read time            = {merged_at_read}")
```

Python facts: `sum(... for a in ACCOUNTS.values())` adds over the three accounts; `round(x)` rounds to the nearest integer (half to even); `sorted(...)` of a list of names gives a list, printed with square brackets and quotes. One day has `86_400` seconds.

## What to write

The exact output: five lines. Compute each number by hand from the data (the products first, then the division and the rounding).

## Example

For `ben` alone: 4 posts a day x 50 followers = 200 inbox rows a day with fan-out on write.

## After you answer

- Which single account is responsible for almost all of the 5,002,200 rows, and what does the hybrid do about it?
- With only 30 followers per account (the chapter's SQLite measurement) both reads were fast and fan-out on write was 30 times more rows for no visible benefit. What threshold rule would you choose from measurements, and when is plain fan-out on read the right and final answer?
